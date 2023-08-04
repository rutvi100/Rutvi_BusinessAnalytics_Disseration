def compare_current_other_sector(sector_data):
    '''
    :param sector_data: data containing the sector attributes
    :return: the sector features for each officer
    '''
    current_sector = sector_data.get("sector", {}).get("current", {}).get(next(iter(sector_data.get("sector", {}).get("current", {}))), {})
    current_sector_code = current_sector.get("sector_code", "")
    current_sector_group_description = current_sector.get("sector_group_description", "").lower()

    other_sectors = sector_data.get("sector", {}).get("other", {})
    other_sector_info = [(sector.get("sector_code", ""), sector.get("sector_group_description", "").lower()) for sector in other_sectors.values()]

    sector_code_hash = hash(current_sector_code)
    sector_group_description_hash = hash(current_sector_group_description)

    compare_sector_code = 1 if any(hash(sector_code) == sector_code_hash for sector_code, _ in other_sector_info) else 0
    compare_sector_group_description = 1 if any(hash(sector_group_description) == sector_group_description_hash for _, sector_group_description in other_sector_info) else 0

    unique_sector_codes = set(
        sector_code for sector_code, _ in other_sector_info if sector_code not in ["unknown", "Undefined"])
    unique_sector_group_descriptions = set(
        sector_group_description for _, sector_group_description in other_sector_info if
        sector_group_description.lower() not in ["unknown", "Undefined"])

    norm_unique_sector_group_description_count = len(unique_sector_group_descriptions) / 21

    return {
        'compare_current_other_sector_code': compare_sector_code,
        'compare_current_other_sector_group_description': compare_sector_group_description,
        'unique_sector_code_count': len(unique_sector_codes),
        'unique_sector_group_description_count': len(unique_sector_group_descriptions),
        'norm_unique_sector_group_description_count': round(norm_unique_sector_group_description_count, 2)
    }
