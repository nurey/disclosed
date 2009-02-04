use strict;
use Agency;
use Exception::Class;
use Getopt::Attribute;

$| = 1; # turn on autoflush;

our $force : Getopt(force 0);
our $all : Getopt(all); 	

my $agency_name = shift @ARGV;
my $agency;

if ( $all ) {
    my $iter = Agency->get_iter();
    while ( my $agency = $iter->() ) {
        eval {
            $agency->scrape_to_csv(force=>$force);
        };
        if ( my $e = Exception::Class->caught('Agency::Exception::AlreadyScraped') ) {
            print $e->error() . " Skipping to next agency\n";
            next;
        }
    	elsif ( my $e = Exception::Class->caught('Agency::Exception') ) {
    	    print $e->error() . "\n";
    	    next;
    	}
    }
    exit 0;
}


eval {
    $agency = Agency->new_from_yml($agency_name);
};
if ( my $e = Exception::Class->caught('Agency::Exception') ) {
    die $e->error();
}
print "Going to scrape " . $agency->{agency_name} . "\n";
$agency->scrape_to_csv(force=>$force);
