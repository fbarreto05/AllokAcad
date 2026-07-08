import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AllokAcad.settings')
django.setup()

from AllokAcads.models import Ambient, Class, Subject, Classroom, Member, Classroom_Preference, Professor_Preference, Schedule_Preference

def setup():
    ambient = Ambient.objects.get(id=4)
    classes = list(ambient.classes.all())
    subjects = list(ambient.subjects.all())
    rooms = list(ambient.classrooms.all())
    professors = list(ambient.members.filter(is_professor=True))
    all_schedules = list(ambient.available_schedules.all())

    if not rooms or not professors or not classes:
        print("Faltam recursos no ambiente de testes.")
        return

    # Clear old preferences
    for c in classes:
        c.prefered_schedules.clear()
        c.ideal_classrooms.clear()
        c.favorite_professors.clear()
    
    for s in subjects:
        s.ideal_classrooms.clear()
        s.favorite_professors.clear()

    # 1. Schedules
    # Give all schedules to all classes
    for c in classes:
        for sched in all_schedules:
            c.prefered_schedules.add(sched)

    # 2. Rooms
    room_A = rooms[0]
    room_B = rooms[1] if len(rooms) > 1 else rooms[0]

    pref_room_A = Classroom_Preference.objects.create(classroom=room_A, classroom_weight=100.0)
    pref_room_B = Classroom_Preference.objects.create(classroom=room_B, classroom_weight=50.0)

    for c in classes:
        c.ideal_classrooms.add(pref_room_A)
        c.ideal_classrooms.add(pref_room_B)

    # 3. Professors
    prof_A = professors[0]
    prof_B = professors[1] if len(professors) > 1 else professors[0]

    pref_prof_A = Professor_Preference.objects.create(professor=prof_A, professor_weight=100.0)
    pref_prof_B = Professor_Preference.objects.create(professor=prof_B, professor_weight=50.0)

    for s in subjects:
        s.favorite_professors.add(pref_prof_A)
        s.favorite_professors.add(pref_prof_B)

    print(f"Setup concluído. Sala VIP: {room_A.name}, Prof VIP: {prof_A.user.name if prof_A.user else prof_A.id}")

if __name__ == '__main__':
    setup()
