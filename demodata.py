from ispportal import db, app

from ispportal.models import *

from faker import Faker

fake = Faker()

def insert_plans():
	with app.app_context():
		bronze = Plans(name = 'bronze', ostemplate = 'local:vztmpl/ubuntu-20.04-standard_20.04-1_amd64.tar.gz', bwlimit = 0, cores = 1, memory = 512, start = 1, rootfs = 'local-lvm:8', storage = 'local-lvm', ostype = 'ubuntu')
		silver = Plans(name = 'silver', ostemplate = 'local:vztmpl/ubuntu-20.04-standard_20.04-1_amd64.tar.gz', bwlimit = 0, cores = 2, memory = 1024, start = 1, rootfs = 'local-lvm:16', storage = 'local-lvm', ostype = 'ubuntu')
		gold = Plans(name = 'gold', ostemplate = 'local:vztmpl/ubuntu-20.04-standard_20.04-1_amd64.tar.gz', bwlimit = 0, cores = 4, memory = 2048, start = 1, rootfs = 'local-lvm:32', storage = 'local-lvm', ostype = 'ubuntu')


		db.session.add(bronze)
		db.session.add(silver)
		db.session.add(gold)
		db.session.commit()

	return 0

def insert_nodes():
	with app.app_context():
		pve = Nodes(name='pve',ipv4address='192.168.0.11', ipv6address='', status='online')

		db.session.add(pve)
		db.session.commit()

	return 0

def generate_fake_news(count=10):
	with app.app_context():
	    for i in range(count):
	        news = News(
	            author=fake.name(),
	            title=fake.sentence(),
	            content=fake.text(),
	            category=fake.random_element(elements=('Announcement', 'News', 'Update', 'Alert')),
	            created_at=fake.date_time_between(start_date='-5d', end_date='now'),
	        )
	        db.session.add(news)
	    db.session.commit()

	return 0

#insert_plans()
#insert_nodes()
generate_fake_news()
