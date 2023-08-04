from hoodsio.tuin.models import CompanyTUIN


def measure_company_parent_child(officer_attributes, other_appointments_dict):
    parent_child = officer_attributes.setdefault("parent_child", {})

    for (
        company_reg_number,
        other_appointment_parent_child_data,
    ) in other_appointments_dict.items():

        officer_attributes["parent_child"][company_reg_number] = []
        # TODO we need to modify the previous step so it saves registration numbers not tuin ids (or maybe both)
        # TODO apparently this needs to be filter oinstead of get, why?
        company_reg_num_tuin_id = str(
            CompanyTUIN.objects.filter(company_number=company_reg_number)[0].id
        )

        if "company_parent_child" in other_appointment_parent_child_data:
            parent_child_data = other_appointment_parent_child_data[
                "company_parent_child"
            ]
        else:
            officer_attributes["parent_child"][company_reg_number] = None
            continue

        for relationship in parent_child_data:
            # TODO we need to change parent_company_child to child and parent_company_parent to parent
            # TODO the logic here is weird, but for now we're only interested in cases where the company_reg_number is
            # either an immediate parent or immediate child, nevermind degree of separation for now
            if "parent_company_child" in relationship:
                if relationship["parent_company_child"] == company_reg_num_tuin_id:
                    officer_attributes["parent_child"][company_reg_number].append(
                        {
                            "child": company_reg_number,
                            "parent": CompanyTUIN.objects.get(
                                id=relationship["parent_company_parent"]
                            ).company_number,
                            "degree_of_separation": relationship.get(
                                "parent_company_degree_of_separation"
                            ),
                            "is_ultimate_parent": 0,
                            "company_is_parent": 0,
                            "company_is_child": 1
                            if relationship.get("parent_company_immediate_parent")
                            else 0,
                        }
                    )

                elif relationship["parent_company_parent"] == company_reg_num_tuin_id:
                    officer_attributes["parent_child"][company_reg_number].append(
                        {
                            "child": CompanyTUIN.objects.get(
                                id=relationship["parent_company_child"]
                            ).company_number,
                            "parent": company_reg_number,
                            "degree_of_separation": relationship.get(
                                "parent_company_degree_of_separation"
                            ),
                            "is_ultimate_parent": 1
                            if relationship.get("parent_company_ultimate_parent")
                            else 0,
                            "company_is_parent": 1
                            if relationship.get("parent_company_immediate_parent")
                            else 0,
                            "company_is_child": 0,
                        }
                    )

            if "child_company_child" in relationship:
                if relationship["child_company_child"] == company_reg_num_tuin_id:
                    officer_attributes["parent_child"][company_reg_number].append(
                        {
                            "child": company_reg_number,
                            "parent": CompanyTUIN.objects.get(
                                id=relationship["child_company_parent"]
                            ).company_number,
                            "degree_of_separation": relationship.get(
                                "parent_company_degree_of_separation"
                            ),
                            "is_ultimate_parent": 0,
                            "company_is_parent": 0,
                            "company_is_child": 1
                            if relationship.get("parent_company_immediate_parent")
                            else 0,
                        }
                    )

                elif relationship["parent_company_parent"] == company_reg_num_tuin_id:
                    officer_attributes["parent_child"][company_reg_number].append(
                        {
                            "child": CompanyTUIN.objects.get(
                                id=relationship["child_company_child"]
                            ).company_number,
                            "parent": company_reg_number,
                            "degree_of_separation": relationship.get(
                                "parent_company_degree_of_separation"
                            ),
                            "company_is_parent": 1,
                            "is_ultimate_parent": 1
                            if relationship.get("parent_company_ultimate_parent")
                            else 0,
                            "company_is_parent": 1
                            if relationship.get("parent_company_immediate_parent")
                            else 0,
                            "company_is_child": 0,
                        }
                    )
