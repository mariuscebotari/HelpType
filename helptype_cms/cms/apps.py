from django.apps import AppConfig

class CmsConfig(AppConfig):
    name = 'cms'

    def ready(self):
        import cms.translation  # Ensure translations are registered
