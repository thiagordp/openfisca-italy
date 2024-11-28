"""This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a Person, a Household…

See https://openfisca.org/doc/key-concepts/variables.html
"""
import numpy as np
# Import from numpy the what you need to apply on OpenFisca's population vectors
# Import from openfisca-core the objects used to code the legislation in OpenFisca
from numpy import maximum as max_
from openfisca_core.periods import MONTH, YEAR
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_country_template.entities import Household, Person


class tuir_income_tax(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Income Tax from TUIR"
    reference = (
        "https://www.brocardi.it/testo-unico-imposte-redditi/titolo-i/capo-i/art11.html"
    )

    def formula(person, period, parameters):
        """Social security contribution.

        The social_security_contribution is computed according to a marginal scale.
        """
        salary = person("salary", period)
        scale = parameters(period).taxes.tuir_income_tax

        print("=" * 50)
        print(f"-- Salary: {salary}")
        print(f"-- TT: {parameters(period).taxes}")
        print(f"-- Scale: {scale}")
        print(f"Children: {person("number_of_children", period)}")
        print(type(scale))
        print(f"-- Calc: {scale.calc(salary)}")
        tax_base = np.array([salary])
        print()
        print(f"==={scale.marginal_rates(tax_base)}")
        print(f"==== --- {scale.marginal_rates(tax_base)[0] * salary[0]}")


        default_income_tax = scale.marginal_rates(tax_base)[0] * salary[0]

        final_income = default_income_tax
        income_type = person("income_type", period)
        IncomeType = (
            income_type.possible_values
        )
        employment = income_type == IncomeType.employment

        if employment:
            final_income = max(0, default_income_tax - 1800)

        number_of_children = person("number_of_children", period).sum()
        if number_of_children > 6:
            final_income = 0

        return final_income


class income_tax(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Income tax"
    reference = (
        "https://law.gov.example/income_tax"  # Always use the most official source
    )

    def formula(person, period, parameters):
        """Income tax.

        The formula to compute the income tax for a given person at a given period
        """

        return person("salary", period) * parameters(period).taxes.income_tax_rate


class social_security_contribution(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Progressive contribution paid on salaries to finance social security"
    # Always use the most official source
    reference = "https://law.gov.example/social_security_contribution"

    def formula(person, period, parameters):
        """Social security contribution.

        The social_security_contribution is computed according to a marginal scale.
        """
        salary = person("salary", period)
        scale = parameters(period).taxes.social_security_contribution

        return scale.calc(salary)


class housing_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR  # This housing tax is defined for a year.
    label = "Tax paid by each household proportionally to the size of its accommodation"
    reference = (
        "https://law.gov.example/housing_tax"  # Always use the most official source
    )

    def formula(household, period, parameters):
        """Housing tax.

        The housing tax is defined for a year, but depends on the `accommodation_size`
        and `housing_occupancy_status` on the first month of the year. Here period
        is a year. We can get the first month of a year with the following shortcut.
        To build different periods, see
        https://openfisca.org/doc/coding-the-legislation/35_periods.html#calculate-dependencies-for-a-specific-period
        """
        january = period.first_month
        accommodation_size = household("accommodation_size", january)

        tax_params = parameters(period).taxes.housing_tax
        tax_amount = max_(
            accommodation_size * tax_params.rate, tax_params.minimal_amount
        )

        # `housing_occupancy_status` is an Enum variable
        occupancy_status = household("housing_occupancy_status", january)
        HousingOccupancyStatus = (
            occupancy_status.possible_values
        )  # Get the enum associated with the variable
        # To access an enum element, we use the `.` notation.
        tenant = occupancy_status == HousingOccupancyStatus.tenant
        owner = occupancy_status == HousingOccupancyStatus.owner

        # The tax is applied only if the household owns or rents its main residency
        return (owner + tenant) * tax_amount
