from datetime import datetime
import json

def format_datetime(dt):
    """Format a datetime object for response"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

def json_serialize(obj):
    """Custom JSON serializer for objects not serializable by default"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def serialize_model(model):
    """Serialize a model instance to dictionary"""
    if hasattr(model, 'to_dict'):
        return model.to_dict()
    
    # Generic serialization for models without to_dict method
    data = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        if isinstance(value, datetime):
            value = format_datetime(value)
        data[column.name] = value
    return data

def deserialize_to_model(data, model_class):
    """Deserialize dictionary to model instance"""
    # Filter out keys that don't exist as columns in the model
    valid_columns = model_class.__table__.columns.keys()
    filtered_data = {k: v for k, v in data.items() if k in valid_columns}
    
    return model_class(**filtered_data)
