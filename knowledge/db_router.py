"""Route knowledge app models to the knowledge database."""


class KnowledgeRouter:
    knowledge_app = "knowledge"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.knowledge_app:
            return "knowledge"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.knowledge_app:
            return "knowledge"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        labels = {obj1._meta.app_label, obj2._meta.app_label}
        if labels <= {self.knowledge_app}:
            return True
        if self.knowledge_app not in labels:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.knowledge_app:
            return db == "knowledge"
        if db == "knowledge":
            return False
        return db == "default"
