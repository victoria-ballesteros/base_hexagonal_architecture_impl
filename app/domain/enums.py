from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class CompanyType(str, Enum):
    TEST_COMPANY = "Compañía de test"


class SocialMedia(str, Enum):
    TEST_SOCIAL_MEDIA = "Red social de test"


class UserStatus(int, Enum):
    INACTIVE = -1
    PENDING = 0
    ACTIVE = 1


class ProgrammingLanguage(str, Enum):
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    PYTHON = "Python"
    JAVA = "Java"
    C_SHARP = "C#"
    PHP = "PHP"
    GO = "GO"
    RUBY = "Ruby"
    RUST = "Rust"
    ELIXIR = "ELixir"
    C_PLUS_PLUS = "C++"
    KOTLIN = "Kotlin"
    SCALA = "Scala"
    SWIFT = "Swift"
    CLOJURE = "Clojure"
    ERLANG = "Erlang"
    HASKELL = "Haskell"
    DART = "Dart"
    PERL = "Perl"
    R = "R"
    JULIA = "Julia"


class TeamRequestStatus(int, Enum):
    DENIED = -1
    PENDING = 0
    ACCEPTED = 1
    DELETED = 2
