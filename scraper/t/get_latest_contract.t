use strict;

use Test::More qw/no_plan/;
use Data::Dumper;

use lib "$ENV{GOAT_HOME}/scraper";
use Agency;

my $agency = Agency->new_from_yml('ec');
print "latest contract date from csv: ", $agency->get_latest_contract_date_from_csv(), "\n";
print "latest contract date: " , $agency->get_latest_contract_date(), "\n";
