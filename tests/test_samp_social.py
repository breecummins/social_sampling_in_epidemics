from social_epi import sampling_social_networks as ssn


def test_read_favites_contact():
    g = ssn.parse_contact_network_file("contact_network_test.txt")
    assert(g.number_of_nodes() == 100)
    assert(g.number_of_edges() == 4950)