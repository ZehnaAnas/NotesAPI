from celery_app import celery_app
from database import SessionLocal,Note

@celery_app.task(bind=True)
def generate_digest(self):
    db = SessionLocal()
    try:
        notes = db.query(Note).all()
        summary = {}
        for note in notes:
            tag = getattr(note, "tag", None)
            summary[tag] = summary.get(tag, 0) + 1
        return {"total_notes":len(notes),"counts_by_tag":summary}
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()