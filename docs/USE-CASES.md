# Use cases by sector

In most sectors, sites would ask for preferences and plans, and could give back a record of what the user did on the site. I think the second half matters more. Offers are usually worth more to the user and are less risky to share, which is why the specification encourages manifests that only offer.

## At a glance

| Sector | Could ask for | Could give back |
|---|---|---|
| Media: news, reading, video, music | `interests`, `languages`, `content_length`, `time_budget`, `locale` for a regional edition | what the user finished, abandoned and saved for later |
| Shopping | `sizes`, `ethical_filters`, `brands_avoided`, `budget_band`, a gift recipient's sizes | purchases kept and returned, confirmed sizes per brand, warranty and return dates |
| Travel | `seat_preferences`, `stay_preferences`, `travel_plans`, `party` as counts, `accessibility_needs` | the itinerary, places stayed, preferred airports |
| Food and recipes | `diet`, `allergies`, `household_size`, `equipment`, `time_budget` | what the user cooked and how they rated it, what they usually have in |
| Learning | prior knowledge, goals, `time_budget`, `languages` | progress by topic, where the user got stuck |
| Software onboarding | `role`, `team_size`, `tools`, how work is tracked today, working hours | workspace conventions, active projects, integrations in use |
| Customer support | `devices`, steps already tried, when the fault started | past ticket outcomes, outages, engineer visits |
| Local services and loyalty | usual order, preferred branch, group size | visit history, reward balance |
| Health and fitness | goals, equipment; anything clinical is protected | appointment dates, workout logs without medical detail |
| Finance and insurance | vehicle, mileage band, named drivers as a count, date of birth | policy summaries, renewal dates, spending by category without amounts |
| Government | preferred language, accessibility needs for the session | appointment dates, reference numbers, deadlines |
| Dating and social | `interests` | almost nothing |
| Games | play style, session length, controls, `accessibility_needs` | achievements, playtime |
| Events and ticketing | `party`, `accessibility_needs`, seating, `budget_band` | tickets held, past events |
| Recruitment | `role`, skills, preferred region, availability | application status, interview dates |

## Where it needs thought

**Media.** "Pick five topics" is the usual first screen, and the feed stays generic until the recommendations catch up. A manifest fixes the first visit. The harder part comes later, when tastes change and the assistant's memory lags behind, which is where the offer of what the user actually finished helps. On a shared family account "interests" covers several people, so the request belongs in the `people` class, and children's profiles are protected.

**Shopping.** A budget is close to financial data, so it is a band and kept for the session only. Buying for a partner is the standard `about: other` case. Weight and body measurements are protected even though they help with fit, so a site should ask for a size rather than a measurement. Confirmed sizes per brand are often more accurate than what the user thinks their size is, which makes them a good offer.

**Travel.** The itinerary is the most useful single offer in any sector: once the user books, their assistant can add the trip to their calendar or anywhere else they choose. Passport details and nationality are immigration data and belong on the site's own signed-in form, never in a manifest. Booking for a parent is `about: other` throughout, and a party's make-up can reveal children, so the manifest should ask for counts only. Loyalty numbers work almost like identifiers, so they stay in the session.

**Food.** This sector shows most clearly why the specification fixes the classes. A vegetarian diet is a preference. An allergy is protected, kept for the session and stated by the user, however convenient it would be for a site to keep it. The recipe example in `examples/` is from this sector.

**Learning.** A placement test is the usual start. Self-assessment is unreliable, so asks are `stated`, offers are `observed`, and the assistant reconciles the two. Learning data about a child is protected, and so are accommodations for a disability.

**Software onboarding.** Work context may sit in a work assistant and personal context in another, and the specification doesn't say which one answers. The consent screen should show which account is sharing. An offer of "our conventions" belongs to the team, so it needs the workspace admin's consent as well as the user's.

**Customer support.** Diagnostic data can reveal more than expected, such as which devices are online and when. Most of it should be kept for the session.

**Local services and loyalty.** A preferred branch is fine, precise location is protected, and live location is forbidden. One company owning several chains is where joining data up is most tempting. Ids are per site and there is no global user id, so the manifest gives that company nothing to join on.

**Health and fitness.** Most of the data is protected, so the form won't get much shorter. What a manifest adds is making the sensitivity of each question visible. Health data shared "to be helpful" can affect insurance, and children's health data is protected twice over. I expect this sector to start with the paste flow, if it adopts at all.

**Finance and insurance.** "Is this your car?" is the standard question about whose data it is, so the vehicle request is `about: either`. Claims history and date of birth are protected and kept for the session. Comparison sites are where offers are most likely to turn into marketing ("you could save £200"), which the specification forbids. A bank needs almost nothing, because it already knows.

**Government.** The legal basis is rarely consent; public bodies usually rely on a statutory task. A manifest is still useful as a statement of purpose and retention that a citizen's assistant can read.

**Dating and social.** Nearly everything is protected or about other people. A site that publishes a manifest asking only for interests has made a public promise, tied to a hash, about what it doesn't ask for.

**Games.** Many players are under 18. An agent that is unsure should assume a child and share nothing beyond basic preferences.

**Events.** Buying for a group is `about: either`. Accessibility needs for a particular venue are protected, but useful for exactly that session.

**Recruitment.** Salary is protected, if it is asked at all, and right to work belongs on the signed-in form. Application status is the record candidates most want, and putting it in their own assistant is a clear gain for them.

## What this suggests about the specification

The four classes covered all fifteen sectors without needing a fifth, and `about: either` came up in four of them, so it is a common case rather than an edge one. Sectors with mostly protected data will probably start with the paste flow and gain transparency before convenience. After the recipe example, a travel site returning an itinerary would make the best end-to-end demonstration.
