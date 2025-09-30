from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///./data/database.sqlite"

# Create the engine
engine = create_engine(DB_URL, echo=False)


def load_video(video_id):
    """Retrieve video with id from the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""SELECT * FROM videos
                                         JOIN users ON users.id = videos.user_id WHERE videos.id = :video_id"""),
                                            {"video_id": video_id})
            video = result.fetchone()
        return {"title": video[1], "description": video[6]}
    except Exception as e:
        return {"error": str(e)}


def add_video(title, year, country, rating, poster, notes, imdb_id, user):
    with engine.connect() as connection:
        try:
            connection.execute(text("""INSERT INTO videos (title, year, country, rating, poster, notes, imdb_id, user_id) 
                                       VALUES (:title, :year, :country, :rating, :poster, :notes, :imdb_id, :user_id)"""),
                               {"title": title, "year": year, "country": country, "rating": rating,
                                "poster": poster, "notes": notes, 'imdb_id': imdb_id, 'user_id': user})
            connection.commit()
            print(f"Video added successfully to your channel.")
        except Exception as e:
            print(f"Error: {e}")


def delete_video(video_id):
    """Delete a video from the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM videos WHERE videos.id = :id"),
                                 {"id": video_id})
            connection.commit()
            print(f"Video has been successfully deleted.")
        except Exception as e:
            print(f"Error: {e}")


def update_video(video_id):
    """Update a videos data in the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("UPDATE videos SET 'notes' = :note WHERE videos.id = :id"),
                                {"id": video_id})
            connection.commit()
            print(f"Video successfully updated.")
        except Exception as e:
            print(f"Error: {e}")
