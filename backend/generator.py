from database import db
from models import Rubro, Entidad, Campo
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, DateTime, Text, MetaData
import os

class TableGenerator:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        self.metadata = MetaData()
    
    def create_empresa_tables(self, empresa_id, rubro_id):
        """Crea tablas físicas para una empresa basado en un rubro"""
        entidades = Entidad.query.filter_by(rubro_id=rubro_id).all()
        tablas_creadas = []
        
        for entidad in entidades:
            table_name = f"emp_{empresa_id}_{entidad.nombre_tabla}"
            campos = Campo.query.filter_by(entidad_id=entidad.id).order_by(Campo.orden).all()
            
            # Crear columnas
            columns = [Column('id', Integer, primary_key=True)]
            for campo in campos:
                col = self._create_column(campo)
                if col is not None:
                    columns.append(col)
            
            # Crear tabla
            table = Table(table_name, self.metadata, *columns, extend_existing=True)
            self.metadata.create_all(self.engine, tables=[table])
            tablas_creadas.append(table_name)
        
        return tablas_creadas
    
    def _create_column(self, campo):
        tipo = self._map_type(campo.tipo)
        kwargs = {
            'nullable': not campo.es_requerido,
        }
        if campo.es_unico:
            kwargs['unique'] = True
        return Column(campo.nombre_fisico, tipo, **kwargs)
    
    def _map_type(self, tipo):
        tipos = {
            'string': String(255),
            'text': Text,
            'integer': Integer,
            'float': Float,
            'boolean': Boolean,
            'date': DateTime,
            'email': String(255),
            'currency': Float
        }
        return tipos.get(tipo, String(255))