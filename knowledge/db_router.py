"""Route knowledge app models to the knowledge database only.

default (users.sqlite3):
  Django auth / sessions / admin + portal learner progress

knowledge (knowledge.sqlite3):
  curriculum outlines, notes, practice items, diseases
"""


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
        if self.knowledge_app in labels and labels - {self.knowledge_app}:
            # Block cross-DB relations between knowledge and user apps
            return False
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.knowledge_app:
            return db == "knowledge"
        if db == "knowledge":
            return False
        return db == "default"
