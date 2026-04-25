import pika
import json
import os
from pydantic import ValidationError
from src.database import SessionLocal
from src.models.workout_type import WorkoutType
from src.etl.schemas import WorkoutTypeRow

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def process_message(ch, method, properties, body):
    try:
        data = json.loads(body)
        row = WorkoutTypeRow(**data)
    except (ValidationError, json.JSONDecodeError):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    db = SessionLocal()
    try:
        existing_type = db.query(WorkoutType).filter(WorkoutType.WorkoutType_Name == row.WorkoutType_Name).first()
        if not existing_type:
            workout_type = WorkoutType(WorkoutType_Name=row.WorkoutType_Name)
            db.add(workout_type)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="workout_type_queue", durable=True)
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue="workout_type_queue", on_message_callback=process_message)
    channel.start_consuming()

if __name__ == "__main__":
    start()