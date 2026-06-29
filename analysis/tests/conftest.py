import os
import sys

# Permite importar los módulos de analysis/ (observables, run_io, ...) al correr pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
