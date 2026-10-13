"""Columns and values the agent is allowed to use."""

YEARS = (2020, 2021, 2022, 2023, 2024)

COLUMNS = ("year", "state", "energy_source", "generation_mwh")

TABLE = "generation"

# Longer names first so "West Virginia" wins over "Virginia".
STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "US": "United States",
}

# Longer phrases first.
ENERGY_SOURCES = (
    ("pumped storage", "Pumped Storage"),
    ("natural gas", "Natural Gas"),
    ("solar thermal and photovoltaic", "Solar Thermal and Photovoltaic"),
    ("hydroelectric conventional", "Hydroelectric Conventional"),
    ("wood and wood derived fuels", "Wood and Wood Derived Fuels"),
    ("other biomass", "Other Biomass"),
    ("other gases", "Other Gases"),
    ("photovoltaic", "Solar Thermal and Photovoltaic"),
    ("hydroelectric", "Hydroelectric Conventional"),
    ("geothermal", "Geothermal"),
    ("petroleum", "Petroleum"),
    ("biomass", "Other Biomass"),
    ("nuclear", "Nuclear"),
    ("solar", "Solar Thermal and Photovoltaic"),
    ("hydro", "Hydroelectric Conventional"),
    ("coal", "Coal"),
    ("wind", "Wind"),
    ("wood", "Wood and Wood Derived Fuels"),
    ("oil", "Petroleum"),
    ("gas", "Natural Gas"),
)

# Asked-for ideas that are not columns or energy sources in this table.
OUTSIDE_SCHEMA = (
    "hydrogen",
    "fusion",
    "battery",
    "revenue",
    "profit",
    "customer",
    "salary",
    "password",
    "ssn",
    "email",
    "invoice",
    "employee",
    "dax",
    "price",
    "cost",
)

ALLOWED_IDENTIFIERS = frozenset({TABLE, *COLUMNS, "sum"})

SQL_KEYWORDS = frozenset(
    {
        "select",
        "from",
        "where",
        "and",
        "or",
        "group",
        "by",
        "order",
        "limit",
        "as",
        "in",
        "not",
        "null",
        "is",
        "desc",
        "asc",
        "on",
        "between",
    }
)

FORBIDDEN_SQL = frozenset(
    {
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "attach",
        "detach",
        "pragma",
        "replace",
        "create",
        "trigger",
        "grant",
        "revoke",
        "exec",
        "execute",
        "load_extension",
        "union",
        "into",
        "vacuum",
        "reindex",
        "analyze",
        "attach",
    }
)
