# -*- coding: UTF-8 -*-
"""ReceiverWmo: socketWmo -> disk, incluant traitement pour les bulletins"""

import gateway
import socketManagerWmo
import bulletinManagerWmo
import socketManager
from socketManager import socketManagerException
import fet

class receiverWmo(gateway.gateway):
    __doc__ = gateway.gateway.__doc__ + \
    """
    ### Ajout de receiver WMO ###

    Implantation du receiver pour un feed Wmo. Il est constitu�
    d'un socket manager Wmo et d'un bulletin manager Wmo.

    Auteur: Louis-Philippe Th�riault
    Date:   Octobre 2004
    """

    def __init__(self,path,options,logger):
        gateway.gateway.__init__(self,path,options,logger)

        self.options = options
        self.establishConnection()

        self.logger.writeLog(logger.DEBUG,"Instanciation du bulletinManagerWmo")

        # Instanciation du bulletinManagerWmo avec la panoplie d'arguments.
        if not options.source:
            self.unBulletinManager = \
                  bulletinManagerWmo.bulletinManagerWmo(
                      self.config.pathTemp,logger, \
                      pathDest = self.config.pathDestination, \
                      pathFichierCircuit = self.config.ficCircuits, \
                      extension = self.config.extension, \
                      mapEnteteDelai = self.config.mapEnteteDelai, \
                      use_pds = self.config.use_pds
                                                          )
        else:
            self.unBulletinManager = \
                  bulletinManagerWmo.bulletinManagerWmo(
                     fet.FET_DATA + fet.FET_RX + options.source, logger, \
                     pathDest = '/dev/null', \
                     pathFichierCircuit = '/dev/null', \
                     extension = options.extension, \
                     mapEnteteDelai = options.mapEnteteDelai )

    def shutdown(self):
        __doc__ = gateway.gateway.shutdown.__doc__ + \
        """### Ajout de receiverWmo ###

           Fermeture du socket et finalisation du tra�tement du
           buffer.

           Utilisation:

                Fermeture propre du programme via sigkill/sigterm

           Visibilit�:  Publique
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """
        gateway.gateway.shutdown(self)

        if self.unSocketManagerWmo.isConnected():
            resteDuBuffer, nbBullEnv = self.unSocketManagerWmo.closeProperly()

            self.write(resteDuBuffer)

        self.logger.writeLog(self.logger.INFO,"Succ�s du tra�tement du reste de l'info")

    def establishConnection(self):
        __doc__ = gateway.gateway.establishConnection.__doc__ + \
        """### Ajout de receiverWmo ###

           establishConnection ne fait que initialiser la connection
           socket.

           Utilisation:

                En encapsulant la connection r�seau par cette m�thode, il est plus
                facile de g�rer la perte d'une connection et sa reconnection.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """

        self.logger.writeLog(self.logger.DEBUG,"Instanciation du socketManagerWmo")

        # Instanciation du socketManagerWmo

        if self.options.source:
            self.unSocketManagerWmo = \
                  socketManagerWmo.socketManagerWmo(self.logger,type='slave', \
                                                         port=self.options.port)
        else:
            self.unSocketManagerWmo = \
                  socketManagerWmo.socketManagerWmo(self.logger,type='slave', \
                                                         port=self.config.localPort)

    def read(self):
        __doc__ =  gateway.gateway.read.__doc__ + \
        """### Ajout de receiverWmo ###

           Le lecteur est le socket tcp, g�r� par socketManagerWmo.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004


           Modification le 25 janvier 2005: getNextBulletins()
           retourne une liste de bulletins.

           Auteur:      Louis-Philippe Th�riault
        """
        if self.unSocketManagerWmo.isConnected():
            try:
                data = self.unSocketManagerWmo.getNextBulletins()
            except socketManager.socketManagerException, e:
                if e.args[0] == 'la connexion est brisee':
                    self.logger.writeLog(self.logger.ERROR,"Perte de connection, tra�tement du reste du buffer")
                    data, nbBullEnv = self.unSocketManagerWmo.closeProperly()
                else:
                    raise
        else:
            raise gateway.gatewayException("Le lecteur ne peut �tre acc�d�")

        self.logger.writeLog(self.logger.VERYVERYVERBOSE,"%d nouveaux bulletins lus",len(data))

        return data

    def write(self,data):
        __doc__ =  gateway.gateway.write.__doc__ + \
        """### Ajout de receiverWmo ###

           L'�crivain est un bulletinManagerWmo.

           Visibilit�:  Priv�e
           Auteur:      Louis-Philippe Th�riault
           Date:        Octobre 2004
        """

        self.logger.writeLog(self.logger.VERYVERYVERBOSE,"%d nouveaux bulletins seront �crits",len(data))

        while True:
            if len(data) <= 0:
                break

            rawBulletin = data.pop(0)

            self.unBulletinManager.writeBulletinToDisk(rawBulletin)

    def reloadConfig(self):
        __doc__ = gateway.gateway.reloadConfig.__doc__
        self.logger.writeLog(self.logger.INFO,'Demande de rechargement de configuration')

        try:

            newConfig = gateway.gateway.loadConfig(self.pathToConfigFile)

            ficCircuits = newConfig.ficCircuits

            # Reload du fichier de circuits
            # -----------------------------
            self.unBulletinManager.reloadMapCircuit(ficCircuits)

            self.config.ficCircuits = ficCircuits

            self.logger.writeLog(self.logger.INFO,'Succ�s du rechargement de la config')

        except Exception, e:

            self.logger.writeLog(self.logger.ERROR,'�chec du rechargement de la config!')

            self.logger.writeLog(self.logger.DEBUG,"Erreur: %s", str(e.args))