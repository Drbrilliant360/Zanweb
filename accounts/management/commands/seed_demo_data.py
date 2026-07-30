from django.core.management.base import BaseCommand
from accounts.models import User, VolunteerProfile
from programs.models import Program, Cohort, ProgramApplication
from volunteering.models import Event, Badge
from donations.models import DonationCampaign, DonationTier
from engagement.models import FAQ, OrgStat


class Command(BaseCommand):
    help = 'Seed the database with demo data for all sections'

    def handle(self, *args, **options):
        if not User.objects.filter(email='admin@example.com').exists():
            admin = User.objects.create_superuser(
                email='admin@example.com', password='admin123',
                first_name='Admin', last_name='User',
            )
            admin.role = 'admin'
            admin.phone_number = '+255 777 000 001'
            admin.save()
            vp, _ = VolunteerProfile.objects.get_or_create(user=admin)
            vp.location = 'Zanzibar'
            vp.save()
            self.stdout.write(self.style.SUCCESS('Created superuser admin@example.com'))
        else:
            self.stdout.write('Superuser already exists')

        if not User.objects.filter(email='volunteer@example.com').exists():
            vol = User.objects.create_user(
                email='volunteer@example.com', password='volunteer123',
                first_name='Amina', last_name='Hassan',
            )
            vol.phone_number = '+255 777 000 002'
            vol.save()
            vp, _ = VolunteerProfile.objects.get_or_create(user=vol)
            vp.location = 'Zanzibar'
            vp.save()
            self.stdout.write(self.style.SUCCESS('Created volunteer volunteer@example.com'))
        else:
            vol = User.objects.get(email='volunteer@example.com')

        if not Program.objects.exists():
            p1 = Program.objects.create(
                name='Youth Leadership Program',
                short_description='Leadership development for young changemakers aged 18-30.',
                description='A comprehensive leadership development program. Includes workshops on public speaking, project management, and community organizing.',
                category='leadership_volunteerism', is_published=True, status='active',
            )
            p2 = Program.objects.create(
                name='Digital Skills for Employment',
                short_description='Hands-on digital literacy training.',
                description='Hands-on training in computer literacy, internet safety, and digital tools to improve employability for youth.',
                category='digital_skills', is_published=True, status='active',
            )
            p3 = Program.objects.create(
                name='Community Health Outreach',
                short_description='Health awareness in rural communities.',
                description='Volunteer-driven health awareness campaigns focusing on hygiene, nutrition, and preventive care.',
                category='health_wellbeing', is_published=True, status='active',
            )
            Cohort.objects.create(program=p1, number=1, name='Cohort 1')
            ProgramApplication.objects.create(
                program=p1, applicant=vol, full_name='Amina Hassan',
                email='volunteer@example.com', phone_number='+255 777 000 002',
                message='I am excited to join this program!', status='pending',
            )
            self.stdout.write(self.style.SUCCESS('Created 3 programs + 1 cohort + 1 application'))
        else:
            self.stdout.write('Programs already exist')

        if not Event.objects.exists():
            Event.objects.create(
                title='Community Clean-Up \u2014 Mbezi Beach',
                description='Join us for a beach clean-up and environmental awareness session.',
                date='2026-08-15', location='Mbezi Beach, Dar es Salaam', capacity=50,
            )
            Event.objects.create(
                title='Youth Digital Skills Bootcamp',
                description='A one-day workshop on digital literacy and online safety.',
                date='2026-09-01', location='TEHAMA Hub, Zanzibar', capacity=30,
            )
            self.stdout.write(self.style.SUCCESS('Created 2 events'))
        else:
            self.stdout.write('Events already exist')

        if not DonationCampaign.objects.exists():
            camp = DonationCampaign.objects.create(
                title='Back to School Drive 2026',
                description='Help us provide school supplies to 500 underprivileged children in Zanzibar.',
                goal_amount=50000.00, is_active=True,
            )
            DonationTier.objects.create(campaign=camp, name='Supporter', amount=10.00, description='Provides a notebook and pen set')
            DonationTier.objects.create(campaign=camp, name='Friend', amount=25.00, description='Provides a school bag')
            DonationTier.objects.create(campaign=camp, name='Champion', amount=50.00, description='Provides a full uniform')
            DonationTier.objects.create(campaign=camp, name='Patron', amount=100.00, description='Sponsors one child for the full term')
            self.stdout.write(self.style.SUCCESS('Created 1 campaign with 4 tiers'))
        else:
            self.stdout.write('Donation campaigns already exist')

        if not FAQ.objects.exists():
            FAQ.objects.create(
                topic='Donations', keywords='donate, donation, money, contribute, give',
                question_example='How can I donate?',
                answer='You can donate via mobile money (M-Pesa, Tigo Pesa, Airtel Money) or bank transfer. Visit our Donate page to contribute.',
                sort_order=1,
            )
            FAQ.objects.create(
                topic='Volunteering', keywords='volunteer, join, register, signup, apply',
                question_example='How do I become a volunteer?',
                answer='Register on our website and fill out the volunteer application. Our team will review and get back to you within 3-5 business days.',
                sort_order=2,
            )
            FAQ.objects.create(
                topic='Programs', keywords='programs, offerings, courses, training',
                question_example='What programs do you offer?',
                answer='We offer youth leadership training, digital skills workshops, community health outreach, and environmental clean-up programs.',
                sort_order=3,
            )
            FAQ.objects.create(
                topic='Eligibility', keywords='eligibility, requirements, who, age, qualify',
                question_example='Who can join your programs?',
                answer='Our programs are open to youth aged 16-35, with a focus on Zanzibar and the wider Tanzania region.',
                sort_order=4,
            )
            self.stdout.write(self.style.SUCCESS('Created 4 FAQ entries'))
        else:
            self.stdout.write('FAQ entries already exist')

        if not OrgStat.objects.exists():
            OrgStat.objects.create(label='Youth Empowered', value='2,500+', icon='users', order=1)
            OrgStat.objects.create(label='Volunteers Active', value='350+', icon='hands', order=2)
            OrgStat.objects.create(label='Communities Reached', value='25+', icon='map-pin', order=3)
            OrgStat.objects.create(label='Programs Delivered', value='60+', icon='book-open', order=4)
            self.stdout.write(self.style.SUCCESS('Created 4 org stats'))
        else:
            self.stdout.write('Org stats already exist')

        if not Badge.objects.exists():
            Badge.objects.create(name='First Steps', icon='\u2b50', description='Completed your first volunteer activity', hours_threshold=1)
            Badge.objects.create(name='Active Volunteer', icon='\U0001f525', description='Logged 40+ hours of service', hours_threshold=40)
            Badge.objects.create(name='Silver Supporter', icon='\U0001f3c6', description='Logged 100+ hours of service', hours_threshold=100)
            Badge.objects.create(name='Gold Champion', icon='\U0001f947', description='Logged 200+ hours of service', hours_threshold=200)
            Badge.objects.create(name='Platinum Leader', icon='\U0001f451', description='Logged 500+ hours of service', hours_threshold=500)
            self.stdout.write(self.style.SUCCESS('Created 5 badges'))
        else:
            self.stdout.write('Badges already exist')

        self.stdout.write(self.style.SUCCESS('Seed complete \u2014 all sections populated'))
