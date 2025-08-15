class NotificationManager:
    """Управление фабриками уведомлений"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.factories = {} # name -> factory
        return cls._instance
    
    def __init__(self):
    # Чтобы избежать повторной инициализации при последующих вызовах
        if not hasattr(self, 'factories'):
            self.factories = {}

    def register_factory(self, name: str, factory):
        """Фабрика: ключ"""
        self.factories[name] = factory

    def get_notification(self, method: str):
        """Создаем уведомление через фабрику"""
        factory = self.factories.get(method)
        if not factory:
            raise ValueError(f'Фабрика не найдена: {method}')
        return factory.create_notification()