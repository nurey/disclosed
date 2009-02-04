#!/opt/local/bin/perl5.10.0

use strict;
use Agency;
use Perl6::Slurp;

my $html = slurp \*STDIN;
Agency->find_table($html);
