use YAML::XS;

my $x = {
    'Environment Canada' => {
        start_url => "http://www.ec.gc.ca/contracts-contrats/default.asp?lang=En&n=168B9233-11",
        headers => ['Date', 'Vendor Name', 'Description', 'Value'],
        entity_keys => ['agency name', 'vendor name', 'reference number', 'contract date', 'description of work', 
                          'contract period', 'delivery date', 'contract value', 'comments'],
        entity_url_key_re => qr/(contractid=.+?)&/,
        entity_table_constraints => { depth=>2, count=>0 },
    }
};

print Dump($x);