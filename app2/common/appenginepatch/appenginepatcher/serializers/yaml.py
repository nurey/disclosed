from django.core.serializers import pyyaml
from python import Deserializer
pyyaml.PythonDeserializer = Deserializer
from django.core.serializers.pyyaml import *
