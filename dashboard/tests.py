from datetime import date
from django.test import TestCase
from AllokAcads.models import User, Member, Activitie, Class, Classroom, ClassroomTP, Subject
from .models import ProfessorStats
class DashboardTest(TestCase):
    def setUpTestData():
        print("Runnig test setup")
        
        user_prof_1 = User.objects.create(
            userid = "123",
            name = "UserProfTest1",
            email = "email@test.com",
            password = "123456",
            birthdate = date(2004, 1, 1)
        )
        member_1 = Member.objects.create(
            user = user_prof_1,
            is_professor = True
        )
        classroomTp_1 = ClassroomTP.objects.create(
            name = "TestClassroomType",
            num_uses = 30
        )
        class_1 = Class.objects.create(
            name = "TestClass",
            number_of_students = 10,
        )
        classroom_1 = Classroom.objects.create(
            name = "TestClassroom",
            classroom_type = classroomTp_1, 
            classroom_capacity = 40
        )
        subject_1 = Subject.objects.create(
            name = "Subject",
        )
        Activitie.objects.create(
            tclass = class_1, 
            tclassroom = classroom_1,
            tprofessor = member_1,
            tsubject = subject_1,
        )

    def test_get_professor_count(self):
        professorStats = ProfessorStats()
        professorStats.get_professor_count()
        count = professorStats.professor_count
        
        self.assertEqual(count, 1, "ERRO")
        