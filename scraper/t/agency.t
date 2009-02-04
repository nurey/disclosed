#!/opt/local/bin/perl5.10.0
use strict;

use Test::More qw/no_plan/;
use Data::Dumper;
use Perl6::Slurp;
use Storable qw/store_fd retrieve/;

use lib '..';
use_ok('Agency');

=head2 STEP 1 download a contract sample

    cd input
    wget "http://www.ceaa.gc.ca/contracts-contrats/default.asp?lang=En&n=BE037596-1&state=details&id=26279A2F&quarter=3&contrdate=2007-12-18&contractid=AD3C4024&fiscal=2007,%202008" -O ceaa_contract_sample.html
    cd ../../
    
=head2 STEP 2 run: ./dump_tables.pl < t/input/ceaa_contract_sample.html

this will tell you the depth and count to use for the entity_table_constraints in the agencies.yaml file. Edit and save the file before going to the next step.

=head2 STEP 3 run: ./store_contract.pl ceaa < t/input/ceaa_contract_sample.html

this will print Dumper output of the contract found in the samle.html. If everything matches up, you should be done. Storable will have written the contract hashref to file at t/input/ceaa_contract_sample.dump.

=cut

sub is_deeply_file {
    my ($hashref, $filename, $message) = @_;
    my $expected_hashref = retrieve $filename;
    is_deeply($hashref, $expected_hashref, $message);
}

# verify Agency::parse_contract by comparing parsed contract to previous stored good parse
sub parse_contract {
    my $agency = shift;
    ok(my $agency_alias = $agency->{alias}, "alias $agency->{alias} found for agency $agency->{agency_name}") or diag(Dumper $agency);
    my $basename = "$ENV{GOAT_HOME}/scraper/t/input/${agency_alias}_contract_sample";
    unless ( -e "$basename.html" && -e "$basename.dump" ) {
        diag "no .html and .dump found; skipping. notes: $agency->{notes}";
        return;
    } 
    ok(my $contract_sample = slurp("$basename.html"), "slurp contract sample");
    ok(my $contract = $agency->parse_contract($contract_sample), "parse sample contract");
    #print Dumper $contract;
    #write_file("$basename.dump", $contract);
    is_deeply_file($contract, "$basename.dump", 'verify sample contract');
}

my $agency_iter = Agency->get_iter();
while ( my $agency = $agency_iter->() ) {
    parse_contract($agency);
}

{
my $cbsa = Agency->new_from_yml_alias('cbsa');
my $cbsa_contracts = slurp "$ENV{GOAT_HOME}/scraper/t/input/cbsa_contracts_2006-2007_q4.html";
ok my $cbsa_contract_urls = $cbsa->parse_contract_urls($cbsa_contracts);
isa_ok($cbsa_contract_urls, 'ARRAY') or BAIL_OUT('not array');
#print "number of cbsa contracts: " . scalar @$cbsa_contract_urls . "\n";
is @$cbsa_contract_urls, 347, 'verify number of contracts';

$cbsa_contracts = slurp "$ENV{GOAT_HOME}/scraper/t/input/cbsa_contracts_2006-2007_q3.html";
ok $cbsa_contract_urls = $cbsa->parse_contract_urls($cbsa_contracts);
#$cbsa->find_table($cbsa_contracts);
isa_ok($cbsa_contract_urls, 'ARRAY') or BAIL_OUT('not array');
#print "number of cbsa contracts: " . scalar @$cbsa_contract_urls . "\n";
is @$cbsa_contract_urls, 184, 'verify number of contracts';
}

{
my $fja = Agency->new_from_yml_alias('fja');
my $fja_contracts = slurp "$ENV{GOAT_HOME}/scraper/t/input/fja_contracts_2007-2008_3.html";
ok my $fja_contract_urls = $fja->parse_contract_urls($fja_contracts);
isa_ok($fja_contract_urls, 'ARRAY') or BAIL_OUT('not array');
#print "number of fja contracts: " . scalar @$fja_contract_urls . "\n";
is @$fja_contract_urls, 11, 'verify number of contracts';
}


# test for _fixup_contract_url
{
    is(Agency->_fixup_contract_url('http://foobar.com/foo.html?bar=baz&amp;'), 
        'http://foobar.com/foo.html?bar=baz&', 
        '_fixup_contract_url for &amp;');
    is(Agency->_fixup_contract_url("http://foobar.com/\nfoo.html"), 
        'http://foobar.com/foo.html', 
        '_fixup_contract_url for newline');    
    is(Agency->_fixup_contract_url('http://foobar.com/foo\bar.html'), 
        'http://foobar.com/foo/bar.html', 
        '_fixup_contract_url for backslash');
}

# test parse_contract_date 
{
    is(Agency->parse_contract_date('2008-12-07'), '2008-12-07', 'parse_contract_date');
    is(Agency->parse_contract_date('12/7/2008'), '2008-12-07', 'parse_contract_date');
}