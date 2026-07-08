from django.test import TestCase
from AllokAcads.models import (
    Class, Classroom, Member, Subject, Activitie, Alocation, Timetable,
    Schedule_Preference, Classroom_Preference, Subject_Preference, Professor_Preference
)
from AllokAcads.metrics import (
    turma_professor_metric, turma_horario_metric, turma_sala_metric,
    professor_horario_metric, professor_disciplina_metric,
    disciplina_sala_metric, disciplina_professor_metric
)

class MetricsTestCase(TestCase):
    def setUp(self):
        # Create common resources
        self.tclass = Class.objects.create(name="Turma A", number_of_students=30)
        self.classroom = Classroom.objects.create(name="Sala 101", classroom_capacity=40)
        
        # In the model, User is required or optional for Member?
        # User is models.ForeignKey('User', on_delete=models.CASCADE, null=True)
        # So we can create a Member without a User, or with user=None.
        self.professor = Member.objects.create(is_professor=True)
        self.subject = Subject.objects.create(name="Matematica")
        
        # Create a timetable and allocation
        self.timetable = Timetable.objects.create(lines_number=5, columns_number=5)
        self.alocation = Alocation.objects.create(line=0, column=0)
        self.timetable.table.add(self.alocation)

    def test_empty_or_none_timetable(self):
        # Testing edge cases
        self.assertEqual(turma_professor_metric(None), 1.0)
        self.assertEqual(turma_professor_metric(Timetable.objects.create()), 1.0)

    def test_no_preferences_defined(self):
        # If there are no preferences, all metrics should return 1.0
        activity = Activitie.objects.create(
            tclass=self.tclass,
            tclassroom=self.classroom,
            tprofessor=self.professor,
            tsubject=self.subject,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        self.assertEqual(turma_professor_metric(self.timetable), 1.0)
        self.assertEqual(turma_horario_metric(self.timetable), 1.0)
        self.assertEqual(turma_sala_metric(self.timetable), 1.0)
        self.assertEqual(professor_horario_metric(self.timetable), 1.0)
        self.assertEqual(professor_disciplina_metric(self.timetable), 1.0)
        self.assertEqual(disciplina_sala_metric(self.timetable), 1.0)
        self.assertEqual(disciplina_professor_metric(self.timetable), 1.0)

    def test_turma_professor_metric(self):
        # Setup preferences: Turma A prefers Professor A (weight 10.0) and Professor B (weight 5.0)
        prof_pref1 = Professor_Preference.objects.create(professor=self.professor, professor_weight=10.0)
        other_prof = Member.objects.create(is_professor=True)
        prof_pref2 = Professor_Preference.objects.create(professor=other_prof, professor_weight=5.0)
        
        self.tclass.favorite_professors.add(prof_pref1, prof_pref2)
        
        # Scenario 1: Preferred professor (weight 10.0) assigned
        activity = Activitie.objects.create(
            tclass=self.tclass,
            tprofessor=self.professor,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        # Should be 10.0 / 10.0 = 1.0
        self.assertEqual(turma_professor_metric(self.timetable), 1.0)
        
        # Scenario 2: Preferred professor (weight 5.0) assigned
        activity.tprofessor = other_prof
        activity.save()
        # Should be 5.0 / 10.0 = 0.5
        self.assertEqual(turma_professor_metric(self.timetable), 0.5)
        
        # Scenario 3: Non-preferred professor assigned
        unpreferred_prof = Member.objects.create(is_professor=True)
        activity.tprofessor = unpreferred_prof
        activity.save()
        # Should be 0.0 / 10.0 = 0.0
        self.assertEqual(turma_professor_metric(self.timetable), 0.0)

    def test_turma_horario_metric(self):
        # Setup preferences: Turma A prefers schedule (0, 0)
        sched_pref = Schedule_Preference.objects.create(line=0, column=0)
        self.tclass.prefered_schedules.add(sched_pref)
        
        activity = Activitie.objects.create(
            tclass=self.tclass,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        # Scenario 1: Correct schedule (0,0) -> 1.0
        self.assertEqual(turma_horario_metric(self.timetable), 1.0)
        
        # Scenario 2: Incorrect schedule (1,1) -> 0.0
        self.alocation.line = 1
        self.alocation.column = 1
        self.alocation.save()
        self.assertEqual(turma_horario_metric(self.timetable), 0.0)

    def test_turma_sala_metric(self):
        # Setup preferences: Turma A prefers Sala 101 (weight 8.0)
        room_pref = Classroom_Preference.objects.create(classroom=self.classroom, classroom_weight=8.0)
        self.tclass.ideal_classrooms.add(room_pref)
        
        activity = Activitie.objects.create(
            tclass=self.tclass,
            tclassroom=self.classroom,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        # Scenario 1: Preferred room assigned -> 1.0
        self.assertEqual(turma_sala_metric(self.timetable), 1.0)
        
        # Scenario 2: Non-preferred room assigned -> 0.0
        other_classroom = Classroom.objects.create(name="Sala 102", classroom_capacity=30)
        activity.tclassroom = other_classroom
        activity.save()
        self.assertEqual(turma_sala_metric(self.timetable), 0.0)

    def test_professor_horario_metric(self):
        # Setup preferences: Professor prefers schedule (0, 0)
        sched_pref = Schedule_Preference.objects.create(line=0, column=0)
        self.professor.prefered_schedules.add(sched_pref)
        
        activity = Activitie.objects.create(
            tprofessor=self.professor,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        # Scenario 1: Correct schedule -> 1.0
        self.assertEqual(professor_horario_metric(self.timetable), 1.0)
        
        # Scenario 2: Incorrect schedule -> 0.0
        self.alocation.line = 2
        self.alocation.column = 2
        self.alocation.save()
        self.assertEqual(professor_horario_metric(self.timetable), 0.0)

    def test_professor_disciplina_metric(self):
        # Setup preferences: Professor prefers Matematica (weight 4.0)
        sub_pref = Subject_Preference.objects.create(subject=self.subject, subject_weight=4.0)
        self.professor.prefered_subjects.add(sub_pref)
        
        activity = Activitie.objects.create(
            tprofessor=self.professor,
            tsubject=self.subject,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        # Scenario 1: Preferred subject assigned -> 1.0
        self.assertEqual(professor_disciplina_metric(self.timetable), 1.0)
        
        # Scenario 2: Non-preferred subject assigned -> 0.0
        other_subject = Subject.objects.create(name="Fisica")
        activity.tsubject = other_subject
        activity.save()
        self.assertEqual(professor_disciplina_metric(self.timetable), 0.0)

    def test_disciplina_sala_metric(self):
        # Setup preferences: Matematica prefers Sala 101 (weight 6.0)
        room_pref = Classroom_Preference.objects.create(classroom=self.classroom, classroom_weight=6.0)
        self.subject.ideal_classrooms.add(room_pref)
        
        activity = Activitie.objects.create(
            tsubject=self.subject,
            tclassroom=self.classroom,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        # Scenario 1: Preferred room assigned -> 1.0
        self.assertEqual(disciplina_sala_metric(self.timetable), 1.0)
        
        # Scenario 2: Non-preferred room assigned -> 0.0
        other_classroom = Classroom.objects.create(name="Sala 103", classroom_capacity=50)
        activity.tclassroom = other_classroom
        activity.save()
        self.assertEqual(disciplina_sala_metric(self.timetable), 0.0)

    def test_disciplina_professor_metric(self):
        # Setup preferences: Matematica prefers Professor (weight 9.0)
        prof_pref = Professor_Preference.objects.create(professor=self.professor, professor_weight=9.0)
        self.subject.favorite_professors.add(prof_pref)
        
        activity = Activitie.objects.create(
            tsubject=self.subject,
            tprofessor=self.professor,
            activities_qtd=1
        )
        self.alocation.activitie.add(activity)
        
        # Scenario 1: Preferred professor assigned -> 1.0
        self.assertEqual(disciplina_professor_metric(self.timetable), 1.0)
        
        # Scenario 2: Non-preferred professor assigned -> 0.0
        other_prof = Member.objects.create(is_professor=True)
        activity.tprofessor = other_prof
        activity.save()
        self.assertEqual(disciplina_professor_metric(self.timetable), 0.0)
