# Core vocabulary (0.1)

Core ids let two sites that want the same thing use the same word, and let an agent match a request to memory it already holds. A site that needs anything else uses an id starting with `x-`.

The ids below are the starting set. From now on, an `x-` id joins the core when two independent sites use it and it fits cleanly into one class.

Where an established name exists, the mapping column gives it: an OpenID Connect standard claim first, then a schema.org term.

## Preference class (may be answered from memory)

| id | meaning | mapping |
|---|---|---|
| `locale` | preferred language and region tag | OIDC `locale` |
| `zoneinfo` | IANA time zone | OIDC `zoneinfo` |
| `languages` | languages the user reads or speaks | schema.org `knowsLanguage` |
| `interests` | topics the user likes | |
| `tone` | preferred writing style, such as formal or casual | |
| `time_budget` | minutes available for the activity | |
| `content_length` | short, medium or long | |
| `diet` | a dietary choice, such as vegetarian, vegan or no coriander. Allergies are protected, and so is a diet kept for religious or medical reasons. | |
| `sizes` | clothing and shoe sizes, with the sizing system | |
| `ethical_filters` | materials or practices the user avoids | |
| `brands_liked` / `brands_avoided` | brand preferences | |
| `budget_band` | expected spend as a band, never a number | |
| `seat_preferences` | window, aisle and so on | |
| `stay_preferences` | what matters in accommodation | |
| `role` | job role in plain words | schema.org `jobTitle` |
| `team_size` | as a band | |
| `tools` | software used day to day | |
| `stack` | technical stack | |
| `devices` | kind and model of each device, with no serial numbers or other identifiers | |
| `equipment` | what the user has to hand, such as kitchen or gym equipment | |

## Plan class (always confirmed with the user)

| id | meaning | mapping |
|---|---|---|
| `travel_plans` | upcoming trips: dates and places | schema.org `Trip` |
| `upcoming_events` | things the user intends to attend or host | schema.org `Event` |
| `purchase_intent` | something the user means to buy soon | |

## People class (always confirmed, never answered from memory)

| id | meaning |
|---|---|
| `household_size` | number of people at home |
| `party` | the group travelling or attending, as counts of adults, children and infants |
| `dependents` | count and age bands only |

Any request with `about: other` or `about: either` is in this class or the protected class, whatever its id.

## Protected class (stated by the user, never answered from memory)

| id | meaning | mapping |
|---|---|---|
| `date_of_birth` | date of birth | OIDC `birthdate` |
| `accessibility_needs` | access requirements | |
| `allergies` | food or other allergies | |
| `health_conditions` | any condition, medication or injury | |
| `income` / `debts` | any financial position | |
| `location_precise` | any location finer than a region or a preferred branch | |
| `nationality` / `right_to_work` | immigration status | |
| `religion` / `politics` / `sexuality` / `ethnicity` | the special categories of personal data | |
| `children` | anything about a specific child | |

SPEC section 4 gives the full list of protected categories. An agent treats a request as protected if the honest answer falls into one of them, whatever the request's id.

## Forbidden

A manifest must not ask for any of these (SPEC section 4.1): credentials or passwords, full payment card numbers, full government identifiers such as a passport, driving licence, National Insurance or Social Security number, biometric data, live location, or the content of the user's conversations with their agent.

## Offer ids

| id | meaning | usual provenance |
|---|---|---|
| `purchases` | what was bought, kept and returned | observed |
| `itinerary` | confirmed bookings | stated |
| `reading_habits` / `viewing_habits` / `listening_habits` | a record of what the user read, watched or listened to | observed |
| `progress` | learning progress and mastery | observed |
| `appointments` | upcoming and past appointments, without clinical detail | stated |
| `service_events` | outages, engineer visits and plan changes | observed |

## Apple privacy label categories

Many people have seen the categories on App Store privacy labels, so this table shows where each one ends up here.

| Apple category | In a Context Manifest |
|---|---|
| Contact Info | Not in the vocabulary. Names, email addresses and postal addresses belong on the site's own forms. |
| Health & Fitness | Protected |
| Financial Info | Protected, apart from `budget_band` |
| Location | Protected if finer than a region or a preferred branch. Live location is forbidden. |
| Sensitive Info | Protected. Biometric data is forbidden. |
| Contacts | Never requested |
| User Content | Never requested |
| Browsing History, Search History | Offers only |
| Identifiers | Never requested. Ids in this specification are per site. |
| Purchases | Preference requests and offers |
| Usage Data | Preference requests and offers |
| Diagnostics | Session-only requests, as in the support example |
| Surroundings, Body | Never requested |
| Other Data | Depends on the request |
