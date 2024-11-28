"""This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a Person, a Household…

See https://openfisca.org/doc/key-concepts/variables.html
"""

# Import from openfisca-core the objects used to code the legislation in OpenFisca
from openfisca_core.holders import set_input_divide_by_period
from openfisca_core.periods import MONTH
from openfisca_core.indexed_enums import Enum
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_country_template.entities import Person


# This variable is a pure input: it doesn't have a formula
class salary(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    # Optional attribute. Allows user to declare a salary for a year. OpenFisca
    # will spread the yearly amount over the months contained in the year.
    set_input = set_input_divide_by_period
    label = "Salary"
    reference = "https://law.gov.example/salary"  # Always use the most official source


class number_of_children(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    set_input = set_input_divide_by_period
    label = "Number of Children"
    reference = "https://law.gov.example/salary"  # ...


class disposable_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Actual amount available to the person at the end of the month"
    # Some variables represent quantities used in economic models, and not
    # defined by law. Always give the source of your definitions.
    reference = "https://stats.gov.example/disposable_income"

    def formula(person, period, _parameters):
        """Disposable income."""
        return (
                +person("salary", period)
                + person("basic_income", period)
                - person("income_tax", period)
                - person("social_security_contribution", period)
        )


class IncomeType(Enum):
    employment = "Income from employment"
    real_estate = "Income from real estate"
    pension = "Income from pension"
    others = "Other types of income"


class income_type(Variable):
    value_type = Enum
    possible_values = IncomeType
    default_value = IncomeType.employment  # Default to employment income
    entity = Person  # or Household, depending on your model
    definition_period = MONTH
    label = "Type of income received by a person"
