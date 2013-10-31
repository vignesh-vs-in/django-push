from django.db import models

class BlobField(models.Field):
	description = "Blob"
	def db_type(self, connection):
		return 'blob'