from django.core.management.base import BaseCommand
from apps.students.models import Student, StudentUDISEInfo

class Command(BaseCommand):
    help = 'Create UDISE information for existing students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Create UDISE info for all students',
        )
        parser.add_argument(
            '--student_id',
            type=int,
            help='Create UDISE info for a specific student by ID',
        )

    def handle(self, *args, **options):
        if options['all']:
            # Get all students without UDISE info
            students = Student.objects.filter(udise_info__isnull=True)
            self.stdout.write(f"Found {students.count()} students without UDISE info")
            
            for student in students:
                self._create_udise_info(student)
                
            self.stdout.write(self.style.SUCCESS(f"Created UDISE info for {students.count()} students"))
        
        elif options['student_id']:
            try:
                student = Student.objects.get(id=options['student_id'])
                self._create_udise_info(student)
                self.stdout.write(self.style.SUCCESS(f"Created UDISE info for student: {student.fullname}"))
            except Student.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Student with ID {options['student_id']} not found"))
        
        else:
            self.stdout.write(self.style.ERROR("Please specify --all or --student_id"))
    
    def _create_udise_info(self, student):
        """Create UDISE info for a student if it doesn't exist"""
        try:
            # Check if UDISE info already exists
            StudentUDISEInfo.objects.get(student=student)
            self.stdout.write(f"UDISE info already exists for {student.fullname}")
        except StudentUDISEInfo.DoesNotExist:
            # Create new UDISE info
            udise_info = StudentUDISEInfo(
                student=student,
                is_udise_student=True,
                mother_tongue="58-HINDI-Bhojpuri",
                nationality="Indian",
                is_indian=True,
                blood_group="Under Investigation"
            )
            udise_info.save()
            self.stdout.write(f"Created UDISE info for {student.fullname}")
