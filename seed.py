import sqlite3

db = sqlite3.connect("database.db")

moments = [
    (None, '05:15', 'calm', '5:15 AM · The world felt still, only birds singing and cold mist touching my face.'),
    (None, '06:20', 'hopeful', '6:20 AM · I watched the sunrise through my window with a cup of tea and big dreams.'),
    (None, '07:35', 'happy', '7:35 AM · My little sister danced while brushing her teeth and laughed at herself.'),
    (None, '08:10', 'nostalgic', '8:10 AM · A song on the radio reminded me of my school farewell day.'),
    (None, '09:42', 'calm', '9:42 AM · I walked alone on the road lined with trees, feeling the peace around me.'),
    (None, '10:15', 'focus', '10:15 AM · Coffee beside laptop, feeling powerful as ideas came together.'),
    (None, '11:03', 'lonely', '11:03 AM · Sitting in a crowd but feeling invisible for a moment.'),
    (None, '11:56', 'happy', '11:56 AM · My old friend called unexpectedly and we laughed like old times.'),
    (None, '12:21', 'chaotic', '12:21 PM · Lunch time rush, loud voices, clinking plates, but somehow beautiful.'),
    (None, '13:14', 'nostalgic', '1:14 PM · The smell of rain on hot ground reminded me of my grandparents house.'),
    (None, '14:48', 'calm', '2:48 PM · Reading a book near the window while sunlight drew patterns on the floor.'),
    (None, '15:20', 'hopeful', '3:20 PM · Saw a kid trying to fly a kite, falling many times but still smiling.'),
    (None, '16:07', 'happy', '4:07 PM · My favorite song played in a random shop and I started humming.'),
    (None, '17:31', 'calm', '5:31 PM · Sunset painted the sky in orange and pink, clouds moving slowly.'),
    (None, '18:05', 'nostalgic', '6:05 PM · Smelled freshly baked bread and remembered my mother baking on Sundays.'),
    (None, '19:42', 'chaotic', '7:42 PM · Traffic lights reflecting on wet roads made everything colorful and alive.'),
    (None, '20:10', 'lonely', '8:10 PM · City noise outside but inside my room was quiet, almost too quiet.'),
    (None, '21:25', 'happy', '9:25 PM · Video call with cousins and sharing memories from our childhood.'),
    (None, '22:17', 'calm', '10:17 PM · Stared at the moon through balcony grills, feeling small and peaceful.'),
    (None, '23:03', 'nostalgic', '11:03 PM · Looking through old photos and smiling at past versions of myself.'),
    (None, '00:45', 'chaotic', '12:45 AM · Thoughts racing, pages filling with sketches I didn’t plan.'),
    (None, '01:18', 'hopeful', '1:18 AM · A message from someone I needed came at the perfect time.'),
    (None, '02:33', 'lonely', '2:33 AM · Silent roads, only streetlights glowing like small stars.'),
    (None, '03:56', 'calm', '3:56 AM · Laying on bed, ceiling fan noise mixing with soft thoughts before sleep.')
]

db.executemany("INSERT INTO moments (user_id, time_value, mood, text) VALUES (?, ?, ?, ?)", moments)
db.commit()
db.close()

print("Inserted 24 demo moments 🌟")
