#!/usr/bin/perl

use strict;

use Text::CSV_XS;
use Data::Dumper;

my $csv = Text::CSV_XS->new();
my $tsv = Text::CSV_XS->new({eol=>"\012", sep_char=>"\t"});

my ($file1, $file2) = @ARGV;

my @headers = (
 'uri',
 'agency name',
 'vendor name',
 'reference number',
 'contract date',
 'description of work',
 'contract period',
 'delivery date',
 'contract value',
 'comments'
 );

open my $in, $file1;
open my $out, ">$file2";
print $out join("\t", @headers);
while (my $row = $csv->getline($in)) {
	$tsv->print($out, $row);
}
close $in;
close $out;
