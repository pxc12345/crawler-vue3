import unittest
from src.models import Person, Student, Rectangle, Circle


class TestModels(unittest.TestCase):
    def test_person_creation(self):
        person = Person("Alice", 25)
        self.assertEqual(person.name, "Alice")
        self.assertEqual(person.age, 25)

    def test_person_greet(self):
        person = Person("Bob", 30)
        self.assertIn("Bob", person.greet())
        self.assertIn("30", person.greet())

    def test_person_is_adult(self):
        adult = Person("Adult", 20)
        minor = Person("Minor", 15)
        self.assertTrue(adult.is_adult())
        self.assertFalse(minor.is_adult())

    def test_student_grades(self):
        student = Student("Charlie", 19, "S001")
        student.add_grade(85)
        student.add_grade(90)
        self.assertEqual(student.get_average_grade(), 87.5)

    def test_rectangle(self):
        rect = Rectangle(4, 4)
        self.assertEqual(rect.area(), 16)
        self.assertEqual(rect.perimeter(), 16)
        self.assertTrue(rect.is_square())

    def test_circle(self):
        circle = Circle(3)
        self.assertAlmostEqual(circle.area(), 28.27, places=2)
        self.assertAlmostEqual(circle.circumference(), 18.85, places=2)


if __name__ == "__main__":
    unittest.main()
