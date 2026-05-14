from src.utils import add, subtract, multiply, divide, fibonacci, is_prime, factorial
from src.models import Person, Student, Rectangle, Circle
from src.algorithms import linear_search, binary_search, bubble_sort


def main():
    print("=== Basic Calculator ===")
    print(f"5 + 3 = {add(5, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")
    print(f"6 * 7 = {multiply(6, 7)}")
    print(f"20 / 4 = {divide(20, 4)}")
    print(f"2^10 = {pow(2, 10)}")
    print(f"5! = {factorial(5)}")
    print()

    print("=== Prime and Fibonacci ===")
    print(f"Is 17 prime? {is_prime(17)}")
    print(f"Is 20 prime? {is_prime(20)}")
    print(f"Fibonacci at position 10: {fibonacci(10)}")
    print()

    print("=== Person and Student ===")
    person = Person("Alice", 25)
    print(person.greet())
    print(f"Is adult? {person.is_adult()}")

    student = Student("Bob", 20, "S12345")
    student.add_grade(85)
    student.add_grade(90)
    student.add_grade(78)
    print(f"Student average grade: {student.get_average_grade():.2f}")
    print()

    print("=== Geometry ===")
    rect = Rectangle(5, 3)
    print(f"Rectangle area: {rect.area()}")
    print(f"Rectangle perimeter: {rect.perimeter()}")
    print(f"Is square? {rect.is_square()}")

    circle = Circle(5)
    print(f"Circle area: {circle.area():.2f}")
    print(f"Circle circumference: {circle.circumference():.2f}")
    print()

    print("=== Search Algorithms ===")
    sorted_list = [1, 3, 5, 7, 9, 11, 13, 15]
    print(f"List: {sorted_list}")
    print(f"Linear search for 7: index {linear_search(sorted_list, 7)}")
    print(f"Binary search for 7: index {binary_search(sorted_list, 7)}")
    print()

    print("=== Sorting Algorithms ===")
    unsorted = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original: {unsorted}")
    print(f"Bubble sort: {bubble_sort(unsorted.copy())}")


if __name__ == "__main__":
    main()
