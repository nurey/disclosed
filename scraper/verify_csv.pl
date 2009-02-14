#!/usr/bin/env perl

use strict;
use 5.10.0;
use Text::CSV_XS;
#my $csv = Text::CSV_XS->new({ binary=>1 });
my $csv = Text::CSV_XS->new({ binary=>0 });

use constant NUM_EXPECTED_COLS => 10; # number of expected columns
use constant REF_NUM_COL => 3; # column number of the reference number

# validation subs get run for each line in the csv file

sub verify_value_col {
    #XXX verify the value column is a float
    my ($fields, $prev_fields) = @_;
    my $value = $fields->[8];
    $value =~ /[\d\.]/g or return "Bad contract value";
    return undef;
}

sub verify_num_expected_cols {
    my ($fields, $prev_fields) = @_;
    # raise error for incorrect number of fields
    scalar @$fields == NUM_EXPECTED_COLS or return "Incorrect number of fields";
    return undef;
}

sub verify_mandatory_cols {
    my ($fields, $prev_fields) = @_;
    # raise error if first 3 fields are empty
    unless ( $fields->[0] && $fields->[1] && $fields->[2] ) {
        return "mandatory field is missing";
    }
    return undef;
}

sub verify_empty_fields {
    my ($fields, $prev_fields) = @_;
    # raise error if there are 4 or more empty fields
    my $missing_fields = 0;
    foreach my $field ( @$fields ) {
        $missing_fields++ if $field eq '';
    }
    if ( $missing_fields >= 4 ) {
        return "4 or more missing fields detected";
    }
    return undef;
}

sub verify_ref_num {
    my ($fields, $prev_fields) = @_;
    # verify reference_number is uniq 
    my $ref_num = $fields->[REF_NUM_COL];
	my $prev_ref_num = $prev_fields->[REF_NUM_COL];
	return undef if $ref_num eq ''; # ignore empty reference numbers
    if ( $ref_num eq $prev_ref_num ) {
        return "duplicate reference number found: $ref_num";
    }
    return undef;
}

my @verify_subs = (
    \&verify_num_expected_cols,
    \&verify_mandatory_cols,
    \&verify_empty_fields,
    \&verify_ref_num,
    \&verify_value_col,
    );
    
my $linenum = 1;
my @prev_fields = ();
while ( my $line = <STDIN> ) {
    $csv->parse($line) or warn "Failed to parse line #$linenum: $line";
    my @fields = $csv->fields();
    foreach my $sub ( @verify_subs ) {
        my $error_msg = $sub->(\@fields, \@prev_fields);
        if ( $error_msg ) {
            say "$error_msg. line #$linenum: $line";
        }
    }
    $linenum++;
	@prev_fields = @fields;
}
