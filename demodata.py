from ispportal import db, app

from ispportal.models import Clients, Plans, Subscriptions

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

insert_plans()