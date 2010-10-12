#!/usr/bin/perl

use File::Basename;

# commit to git only those files that have added more lines than removed, according to git diff --numstat
open my $numstat, "git diff --numstat $ENV{GOAT_HOME}/data |" or die $!;
while ( my $line = <$numstat> ) {
    chomp $line;
    my ($added, $removed, $path) = split /\t/, $line;
    if ( $added > $removed ) {
        push @candidates, basename $path;
    }
}
close $numstat;

my $candidates = join " ", @candidates;
print $candidates;

#print join "\n", @candidates;
#print "\n";
