#!/opt/local/bin/perl5.10.0

use strict;
use Agency;
use Perl6::Slurp;
use Data::Dumper;
use Storable qw/store_fd/;

my $alias = shift @ARGV or die "Usage:\n $0 csc < csc_contract_sample.html\n";
my $html = slurp \*STDIN;
my $agency = Agency->new_from_yml_alias($alias);
my $contract = $agency->parse_contract($html);

print Dumper $contract;

my $dump_file = "t/input/${alias}_contract_sample.dump";
write_file($dump_file, $contract);
print "Storable wrote to file $dump_file\n";

sub write_file {
    my ($filename, $hashref) = @_;
    open my $fh, ">$filename" or die $!;
    store_fd $hashref, $fh;
    close $fh;
}
