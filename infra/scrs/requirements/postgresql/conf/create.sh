if [ -f "/var/lib/postgresql/postgres.check" ]
then
	sudo service postgresql start
	tail -f /dev/null
else
	sed "s/DB_USER/$DB_USER/g" /tmp/create.sql > tmp1; cat tmp1 > /tmp/create.sql; rm tmp1
	sed "s/DB_PASS/$DB_PASS/g" /tmp/create.sql > tmp1; cat tmp1 > /tmp/create.sql; rm tmp1
	sed "s/DB_DB/$DB_DB/g" /tmp/create.sql > tmp1; cat tmp1 > /tmp/create.sql; rm tmp1
	sudo service postgresql start
	sudo -u postgres psql -f /tmp/create.sql
	sudo touch "/var/lib/postgresql/postgres.check"
	tail -f /dev/null
fi
