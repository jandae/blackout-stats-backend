from json_parser import separate

child_item = {}
child_item['id'] = 'NULL'
child_item['post_id'] = '6666666'
child_item['parent'] = 0
child_item['area'] = ''
child_item['coverage'] = 'full'

def test_separate():
    child_item['area'] = 'A And Whole Of B And Whole Of C'
    separated = separate('And Whole Of', child_item, [], 'partial')
    assert len(separated) == 3, "Should be 3"
    assert separated[0]['area'] == 'A', "Should be A"
    assert separated[1]['area'] == 'B', "Should be B"
    assert separated[2]['area'] == 'C', "Should be C"

def test_separate_3():
    child_item['area'] = 'A And Whole Of B And Parts Of C'
    separated = separate('And Parts Of', child_item, [], 'partial')
    assert len(separated) == 3, "Should be 3"
    assert separated[0]['area'] == 'A', "Should be A"
    assert separated[1]['area'] == 'B', "Should be B"
    assert separated[2]['area'] == 'C', "Should be C"

def test_separate_4():
    child_item['area'] = 'A And Whole Of B And Parts Of C'
    separated = separate('And Parts Of', child_item, [], 'partial')
    print(separated)
    assert len(separated) == 3, "Should be 3"
    assert separated[0]['area'] == 'A', "Should be A"
    assert separated[1]['area'] == 'B', "Should be B"
    assert separated[2]['area'] == 'C', "Should be C"
    assert separated[2]['coverage'] == 'partial', "Should be Partial"

if __name__ == "__main__":
    # test_separate('A And Whole Of B And Whole Of C')
    # test_separate()
    # test_separate_3()
    test_separate_4()
    print("Everything passed")