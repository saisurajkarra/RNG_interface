# utils/region_tagging.py

def assign_region(state):
    west = ['CA', 'OR', 'WA', 'NV', 'ID', 'AZ', 'AK', 'HI', 'MT', 'WY', 'UT', 'CO', 'NM']
    midwest = ['ND', 'SD', 'NE', 'KS', 'MN', 'IA', 'MO', 'WI', 'IL', 'IN', 'OH', 'MI']
    south = ['TX', 'OK', 'AR', 'LA', 'KY', 'TN', 'MS', 'AL', 'GA', 'FL', 'SC', 'NC', 'VA', 'WV']
    northeast = ['PA', 'NY', 'NJ', 'DE', 'MD', 'CT', 'RI', 'MA', 'VT', 'NH', 'ME']

    state = str(state).upper()

    if state in west:
        return 'West'
    elif state in midwest:
        return 'Midwest'
    elif state in south:
        return 'South'
    elif state in northeast:
        return 'Northeast'
    return 'Unknown'
