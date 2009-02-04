#!/opt/local/bin/perl5.10.0

use strict;
use Agency;
use Perl6::Slurp;
#use 5.10.0;

my $alias = shift @ARGV or die "Usage:\n $0 csc < csc_contract_sample.html\n";
my $html = slurp \*STDIN;
my $agency = Agency->new_from_yml_alias($alias);
my ($depth, $count, $key) = $agency->find_contract_table($html);
print "found contract with key '$key' at depth $depth, count $count\n";