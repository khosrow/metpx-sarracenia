# -*- coding: UTF-8 -*-
import gateway
import socketManagerAm
import bulletinManagerAm
import bulletinAm
from socketManager import socketManagerException
from DiskReader import DiskReader
from MultiKeysStringSorter import MultiKeysStringSorter
import fet

class senderAm(gateway.gateway):
    __doc__ = gateway.gateway.__doc__ + \
    """
    #### CLASSE senderAm ####

    Nom:
    senderAm

    Paquetage:

    Statut:
    Classe concrete

    Responsabilites:
    -Lire des bulletins en format Am;
    -Envoyer les bulletins Am lus selon un ordre de priorite dans une arborescence;
    -Communiquer en respectant le protocole Am.

    Attributs:
    Attribut de la classe parent gateway

    Methodes:
    Methodes de la classe parent gateway

    Auteur:
    Pierre Michaud

    Date:
    Janvier 2005
    """

    def __init__(self,path,options,logger):
        """
        Nom:
        __init__

        Parametres d'entree:
        -path:  repertoire ou se trouve la configuration
        -logger:        reference a un objet log

        Parametres de sortie:
        -Aucun

        Description:
        Instancie un objet senderAm.

        Auteur:
        Pierre Michaud

        Date:
        Janvier 2005
        """
        gateway.gateway.__init__(self,path,options,logger)
        self.establishConnection()
        self.options = options

        # Instanciation du bulletinManagerAm selon les arguments issues du fichier
        # de configuration
        self.logger.writeLog(logger.DEBUG,"Instanciation du bulletinManagerAm")
        if options.client:
            self.unBulletinManagerAm = \
                 bulletinManagerAm.bulletinManagerAm(
                 fet.FET_DATA + fet.FET_TX + options.client, logger)
            self.config.remoteHost = options.host
            self.config.localPort = options.port
            self.config.timeout    = options.connect_timeout

        else:
            self.unBulletinManagerAm = \
                 bulletinManagerAm.bulletinManagerAm(self.config.pathTemp,logger)
        self.listeFichiersDejaChoisis = []
        self.reader = None

    def shutdown(self):
        __doc__ = gateway.gateway.shutdown.__doc__ + \
        """
        ### senderAm ###
        Nom:
        shutdown

        Parametres d'entree:
        -Aucun

        Parametres de sortie:
        -Aucun

        Description:
        Termine proprement l'existence d'un senderAm.  Les taches en cours sont terminees
        avant d'eliminer le senderAm.

        Nom:
        Pierre Michaud

        Date:
        Janvier 2005
        """
        gateway.gateway.shutdown(self)

        resteDuBuffer, nbBullEnv = self.unSocketManagerAm.closeProperly()

        self.write(resteDuBuffer)

        self.logger.writeLog(self.logger.INFO,"Le senderAm est mort.  Traitement en cours reussi.")

    def establishConnection(self):
        __doc__ = gateway.gateway.establishConnection.__doc__ + \
        """
        ### senderAm ###
        Nom:
        establishConnection

        Parametres d'entree:
        -Aucun

        Parametres de sortie:
        -Aucun

        Description:
        Initialise la connexion avec le destinataire.

        Nom:
        Pierre Michaud

        Date:
        Janvier 2005
        """

        # Instanciation du socketManagerAm
        self.logger.writeLog(self.logger.DEBUG,"Instanciation du socketManagerAm")

        if self.options.client:
            self.unSocketManagerAm = \
                 socketManagerAm.socketManagerAm(
                         self.logger,type='master', \
                         port=self.options.port,\
                         remoteHost=self.options.host,
                         timeout=self.options.connect_timeout)
        else:
            self.unSocketManagerAm = \
                 socketManagerAm.socketManagerAm(self.logger,type='master', \
                      port=self.config.remoteHost[1],\
                      remoteHost=self.config.remoteHost[0],
                      timeout=self.config.timeout)

    def read(self):
        __doc__ =  gateway.gateway.read.__doc__ + \
        """
        ### senderAm ###
        Nom:
        read

        Parametres d'entree:
        -Aucun

        Parametres de sortie:
        -data: dictionnaire du contenu d'un fichier selon son chemin absolu

        Description:
        Lit les bulletins contenus dans un repertoire.  Le repertoire
        contient les bulletins de la priorite courante.

        Nom:
        Pierre Michaud

        Date:
        Janvier 2005
        """
        if not self.options.client:
            self.reader = DiskReader(
                self.config.rootPath,
                eval(self.config.sorter))
            self.reader.sort()
            return(self.reader.getFilesContent(self.config.fileNumber))
        else:
            self.reader = DiskReader(
                 fet.FET_DATA + fet.FET_TX + self.options.client,
                 True, # name validation
                 self.logger,
                 eval(self.options.sorter))
            self.reader.sort()
            return(self.reader.getFilesContent(fet.clients[self.options.client][5]))

        """
        data = []

        #lecture de la selection precedente
        liste = self.unBulletinManagerAm.getListeNomsFichiersAbsolus()

        #si rien n'a ete envoye lors de la derniere lecture,
        #on considere le dernier envoi non vide effectue
        if len(liste)>=1:
                self.listeFichiersDejaChoisis = self.unBulletinManagerAm.getListeNomsFichiersAbsolus()

        try:
                #determination des bulletins a lire et lecture de leur contenu brut
                data = self.unBulletinManagerAm.readBulletinFromDisk(self.config.listeRepertoires,self.listeFichiersDejaChoisis,priorite=1)

                return data

        except Exception, e:
                self.logger.writeLog(self.logger.ERROR,"senderAm.read(): Erreur lecture: %s",str(e.args))
                raise
        """

    def write(self,data):
        __doc__ =  gateway.gateway.write.__doc__ + \
        """
        ### senderAm ###
        Nom:
        write

        Parametres d'entree:
        -data: dictionnaire du contenu d'un fichier selon son chemin absolu

        Parametres de sortie:
        -Aucun

        Description:
        Genere les bulletins en format AM issus du dictionnaire data
        et les ecrit au socket approprie.

        Nom:
        Pierre Michaud

        Date:
        Janvier 2005
        """

        #"""
        self.logger.writeLog(self.logger.DEBUG,"%d nouveaux bulletins sont envoyes",len(data))

        for index in range(len(data)):
            try:
                rawBulletin = data[index]
                unBulletinAm = bulletinAm.bulletinAm(rawBulletin,self.logger,finalLineSeparator='\r\r\n')
                succes = self.unSocketManagerAm.sendBulletin(unBulletinAm)
                #si le bulletin a ete envoye correctement, le fichier est efface
                if succes:
                    self.logger.writeLog(self.logger.INFO,"bulletin %s envoye ", self.reader.sortedFiles[index])
                    self.unBulletinManagerAm.effacerFichier(self.reader.sortedFiles[index])
                    self.logger.writeLog(self.logger.DEBUG,"senderAm.write(..): Effacage de " + self.reader.sortedFiles[index])
                else:
                    self.logger.writeLog(self.logger.INFO,"bulletin %s: probleme d'envoi ", self.reader.sortedFiles[index])
            except Exception, e:
                if e==104 or e==110 or e==32 or e==107:
                    self.logger.writeLog(self.logger.ERROR,"senderAm.write(): la connexion est rompue: %s",str(e.args))
                else:
                    self.logger.writeLog(self.logger.ERROR,"senderAm.write(): erreur: %s",str(e.args))
                raise
        #"""
        """
        self.logger.writeLog(self.logger.DEBUG,"%d nouveaux bulletins sont envoyes",len(data))
        for key in data:
                try:
                        #creation du bulletin am
                        rawBulletin = data[key]
                        unBulletinAm = bulletinAm.bulletinAm(rawBulletin,self.logger)
                        #envoi du bulletin am
                        succes = self.unSocketManagerAm.sendBulletin(unBulletinAm)

                        #si le bulletin a ete envoye correctement, le fichier
                        #est efface, sinon le bulletin est retire de la liste
                        #de fichier deja envoyes
                        if succes:
                                self.logger.writeLog(self.logger.INFO,"bulletin %s envoye ",key)
                                self.unBulletinManagerAm.effacerFichier(key)
                                self.logger.writeLog(self.logger.DEBUG,"%s est efface",key)
                        else:
                                self.logger.writeLog(self.logger.INFO,"bulletin %s: probleme d'envoi ",key)
                                if self.listeFichiersDejaChoisis.count(key)>0:
                                        self.listeFichiersDejaChoisis.remove(key)

                except Exception, e:
                        if e==104 or e==110 or e==32 or e==107:
                                self.logger.writeLog(self.logger.ERROR,"senderAm.write(): la connexion est rompue: %s",str(e.args))
                        else:
                                self.logger.writeLog(self.logger.ERROR,"senderAm.write(): erreur: %s",str(e.args))
                        raise
        """