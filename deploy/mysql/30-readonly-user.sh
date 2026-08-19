#!/bin/sh
set -eu

mysql --protocol=socket -uroot -p"${MYSQL_ROOT_PASSWORD}" <<'SQL'
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'ead_ro'@'%';
GRANT SELECT ON `ead_db`.* TO 'ead_ro'@'%';
FLUSH PRIVILEGES;
SQL
