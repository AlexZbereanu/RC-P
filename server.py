import const


class ModbusServer(object):

    def __init__(self, host='localhost', port=const.PORT):
        self.host = host
        self.port = port
        self.running = False
        self.service = None

    def start(self):
        pass

    def stop(self):
        if self.is_run:
            self.service.shutdown()
            self.service.server_close()

    def is_run(self):
        return self.running
