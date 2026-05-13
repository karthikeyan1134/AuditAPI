# Developer Impact Report

**Generated:** 2026-05-13 11:00 UTC
**Pipeline Version:** 1.0.0
**Lookback Window:** 90 days

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total changes ingested | 330 |
| Recent entries (after 90-day filter) | 330 |
| Breaking or high-risk changes | 43 |
| Affected functions | 0 |
| Sources monitored | 3 |
| Security alerts | 0 |

### Sources Monitored

- **Stripe Node.js SDK** (`stripe_node`): 162 entries classified
- **OpenAI Python SDK** (`openai_python`): 124 entries classified
- **Twilio Changelog** (`twilio`): 44 entries classified

---

## Breaking Changes by Source

### Stripe Node.js SDK

#### 🟡 ⚠️ Add support for new values `fee_credit_funding`, `inbound_transfer_reversal`, and `inbound_transfer` on enum `Bala...

- **Entry ID:** `stripe_node-008`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds new values to an enum, which is explicitly marked as breaking and affects the data model and billing.

#### 🟡 ⚠️ Add support for new values `phantom_cash` and `usdt` on enums `Charge.payment_method_details.crypto.token_currency...

- **Entry ID:** `stripe_node-010`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds new values to an enum for crypto token currency, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new values `fo_vat`, `gi_tin`, `it_cf`, and `py_ruc` on enums `Checkout.Session.customer_details.t...

- **Entry ID:** `stripe_node-018`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds new values to an enum for customer tax IDs, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `Checkout.Session.payment_method_options.pix.setup_future_usage` and `PaymentIntent.payment_method_...

- **Entry ID:** `stripe_node-019`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a response field type from a literal to an enum, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new value `sunbit` on enums `ConfirmationToken.payment_method_preview.type` and `PaymentMethod.type`

- **Entry ID:** `stripe_node-021`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to response objects, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new values `pix` and `upi` on enums `Invoice.payment_settings.payment_method_types` and `Subscript...

- **Entry ID:** `stripe_node-027`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds new payment method types to invoice and subscription response objects, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new value `fulfillment_error` on enum `Issuing.Card.cancellation_reason`

- **Entry ID:** `stripe_node-030`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new cancellation reason to an Issuing Card enum, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new value `fulfillment_error` on enum `Issuing.Card.replacement_reason`

- **Entry ID:** `stripe_node-031`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new replacement reason to an Issuing Card enum, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new value `sunbit` on enums `PaymentIntent.excluded_payment_method_types` and `SetupIntent.exclude...

- **Entry ID:** `stripe_node-034`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to PaymentIntent and SetupIntent excluded types, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new value `sunbit` on enum `PaymentLink.payment_method_types`

- **Entry ID:** `stripe_node-037`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to PaymentLink response objects, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new values `low`, `not_assessed`, and `unknown` on enum `Radar.PaymentEvaluation.signals.fraudulen...

- **Entry ID:** `stripe_node-038`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds new risk level values to a Radar PaymentEvaluation enum, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Add support for new value `account` on enum `Radar.ValueList.item_type`

- **Entry ID:** `stripe_node-040`
- **Version:** 22.1.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** This entry adds a new item type to Radar ValueList response objects, explicitly marked as breaking and affecting the data model.

#### 🟠 [#2619](https://github.com/stripe/stripe-node/pull/2619) Improved TypeScript support in the Node SDK

- **Entry ID:** `stripe_node-065`
- **Version:** 22.0.0
- **Type:** enhancement
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry describes a general improvement to TypeScript support, which is an enhancement but introduces significant breaking changes.

#### 🟠 Removed top-level “stripe” ambient module.

- **Entry ID:** `stripe_node-067`
- **Version:** 22.0.0
- **Type:** deprecation
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry removes a top-level ambient module, which is a deprecation that will break existing code relying on it.

#### 🟠 ⚠️ `Stripe.StripeContext` is no longer exported as a type.

- **Entry ID:** `stripe_node-068`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a type is no longer exported and provides an alternative, classifying it as a breaking change with high risk.

#### 🟠 ⚠️ `Stripe.errors.StripeError` is no longer a type.

- **Entry ID:** `stripe_node-069`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a type is no longer available and provides alternatives, classifying it as a breaking change with high risk.

#### 🔴 ⚠️ CJS entry point no longer exports .default or .Stripe as separate properties.

- **Entry ID:** `stripe_node-070`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a change in CJS export behavior, which is a critical breaking change for CJS users.

#### 🔴 ⚠️ Stripe import is now a true ES6 class.

- **Entry ID:** `stripe_node-071`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a change in how the Stripe client is instantiated, which is a critical breaking change.

#### 🟠 [#2645](https://github.com/stripe/stripe-node/pull/2645) ⚠️ Remove `stripeMethod` and standardize how function args a...

- **Entry ID:** `stripe_node-072`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states the removal of `stripeMethod` and standardization of argument handling, classifying it as a breaking change with high risk.

#### 🟠 ⚠️ Refactor how incoming method arguments are parsed.

- **Entry ID:** `stripe_node-073`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a refactor of method argument parsing, classifying it as a breaking change with high risk.

#### 🔴 ⚠️ Remove support for providing callbacks to API methods.

- **Entry ID:** `stripe_node-074`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states the removal of callback support for API methods, which is a critical breaking change.

#### 🟠 ⚠️ Remove support for passing a plain API key as a function arg.

- **Entry ID:** `stripe_node-075`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** True
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states the removal of plain API key arguments, which is a breaking change affecting authentication with high risk.

#### 🔴 ⚠️ Keys from `params` and `options` objects are no longer mixed.

- **Entry ID:** `stripe_node-076`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a change in how `params` and `options` are handled in API methods, which is a critical breaking change.

#### 🟠 ⚠️ Removed methods from `StripeResource`: `createFullPath`, `createResourcePathWithSymbols`, `extend`, `method` and `...

- **Entry ID:** `stripe_node-077`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states the removal of several methods from `StripeResource`, classifying it as a breaking change with high risk.

#### 🟠 [#2643](https://github.com/stripe/stripe-node/pull/2643) ⚠️ Removed per-request host override.

- **Entry ID:** `stripe_node-078`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states the removal of per-request host override, which is a breaking change with high risk.

#### 🟠 [#2619](https://github.com/stripe/stripe-node/pull/2619) Improved TypeScript support in the Node SDK

- **Entry ID:** `stripe_node-079`
- **Version:** 22.0.0
- **Type:** enhancement
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry describes a general improvement to TypeScript support, which is an enhancement but introduces significant breaking changes.

#### 🟡 [#2638](https://github.com/stripe/stripe-node/pull/2638) Converted V2/Amount.ts to V2/V2Amount.ts

- **Entry ID:** `stripe_node-080`
- **Version:** 22.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry describes a file rename, which is a breaking change for any code directly importing that file.

#### 🔴 ⚠️ **Breaking change:** [#2617](https://github.com/stripe/stripe-node/pull/2617) Add decimal_string support with vend...

- **Entry ID:** `stripe_node-083`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry explicitly states a breaking change related to `decimal_string` support, which affects billing and the data model with critical risk.

#### 🔴 All `decimal_string` fields changed type from `string` to `Stripe.Decimal` in both request params and response objects.

- **Entry ID:** `stripe_node-084`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry details a critical breaking change where `decimal_string` fields change type, requiring significant code updates and affecting billing and the data model.

#### 🔴 Checkout.Session: `currency_conversion.fx_rate`

- **Entry ID:** `stripe_node-085`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 Climate.Order: `metric_tons`; **Climate.Product**: `metric_tons_available`

- **Entry ID:** `stripe_node-086`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 CreditNoteLineItem: `unit_amount_decimal`

- **Entry ID:** `stripe_node-087`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 InvoiceItem: `quantity_decimal`, `unit_amount_decimal`

- **Entry ID:** `stripe_node-088`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 InvoiceLineItem: `quantity_decimal`, `unit_amount_decimal`

- **Entry ID:** `stripe_node-089`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 Issuing.Authorization / **Issuing.Transaction** (and TestHelpers): `quantity_decimal`, `unit_cost_decimal`, `gross_am...

- **Entry ID:** `stripe_node-090`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 Plan: `amount_decimal`, `flat_amount_decimal`, `unit_amount_decimal`

- **Entry ID:** `stripe_node-091`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 Price: `unit_amount_decimal`, `flat_amount_decimal` (including `currency_options` and `tiers`)

- **Entry ID:** `stripe_node-092`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🔴 V2.Core.Account / **V2.Core.AccountPerson**: `percent_ownership`

- **Entry ID:** `stripe_node-093`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting the data model.

#### 🔴 Request params on **Invoice**, **Product**, **Quote**, **Subscription**, **SubscriptionItem**, **SubscriptionSchedule...

- **Entry ID:** `stripe_node-094`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry is part of a critical breaking change related to `decimal_string` type changes, affecting billing and the data model.

#### 🟠 ⚠️ **Breaking change:** [#2618](https://github.com/stripe/stripe-node/pull/2618)[#2616](https://github.com/stripe/str...

- **Entry ID:** `stripe_node-095`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a breaking change that throws an error for incorrect webhook parsing, classifying it as a breaking change with high risk.

#### 🟡 ⚠️ **Breaking change:** [#2604](https://github.com/stripe/stripe-node/pull/2604) Add new OAuth Error classes

- **Entry ID:** `stripe_node-096`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** True
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states a breaking change by adding new OAuth error classes, which affects authentication and carries a medium breaking risk.

#### 🔴 ⚠️ **Breaking change:** [#2609](https://github.com/stripe/stripe-node/pull/2609) Drop support for Node 16

- **Entry ID:** `stripe_node-097`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** critical
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** This entry explicitly states dropping support for Node 16, which is a critical breaking change for users on that version.

#### 🟠 Generated changes from [#2611](https://github.com/stripe/stripe-node/pull/2611), [#2620](https://github.com/stripe/st...

- **Entry ID:** `stripe_node-100`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry indicates generated breaking changes from multiple pull requests, implying significant API and data model impacts.

#### 🟡 Add support for `upi_payments` on `Account.capabilities`, `AccountCreateParams.capabilities`, and `AccountUpdateParam...

- **Entry ID:** `stripe_node-101`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds support for new payment capabilities, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `upi` on `Charge.payment_method_details`, `Checkout.Session.payment_method_options`, `Checkout.Sessio...

- **Entry ID:** `stripe_node-102`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds support for a new payment method, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `tempo` on enums `Charge.payment_method_details.crypto.network`, `PaymentAttemptRecord.paym...

- **Entry ID:** `stripe_node-103`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new value to a crypto network enum, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `integration_identifier` on `Checkout.SessionCreateParams` and `Checkout.Session`

- **Entry ID:** `stripe_node-104`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new integration identifier to Checkout Sessions, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `upi` on enums `Checkout.SessionCreateParams.excluded_payment_method_types`, `PaymentIntent...

- **Entry ID:** `stripe_node-105`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to excluded types, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `crypto` on `Checkout.SessionCreateParams.payment_method_options`

- **Entry ID:** `stripe_node-106`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds support for crypto payment method options, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `upi` on enum `Checkout.SessionCreateParams.payment_method_types`

- **Entry ID:** `stripe_node-107`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to Checkout Session creation parameters, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `pending_invoice_item_interval` on `Checkout.SessionCreateParams.subscription_data`

- **Entry ID:** `stripe_node-108`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new field to Checkout Session subscription data, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new values `elements`, `embedded_page`, `form`, and `hosted_page` on enums `Checkout.Session.ui_mode`...

- **Entry ID:** `stripe_node-109`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** This entry adds new UI mode values to Checkout Session enums, explicitly marked as breaking and affecting the data model.

#### 🟡 Add support for new value `marine_carbon_removal` on enum `Climate.Supplier.removal_pathway`

- **Entry ID:** `stripe_node-110`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new value to a Climate Supplier enum, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `upi` on enums `ConfirmationTokenCreateParams.testHelpers.payment_method_data.type`, `Payme...

- **Entry ID:** `stripe_node-111`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to confirmation token and payment intent creation/update parameters, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `upi` on enums `ConfirmationToken.payment_method_preview.type` and `PaymentMethod.type`

- **Entry ID:** `stripe_node-112`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to confirmation token and payment method response objects, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `metadata` on `CreditNoteCreateParams.lines[]`, `CreditNoteLineItem`, `CreditNotePreviewLinesParams.l...

- **Entry ID:** `stripe_node-113`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds metadata support to credit note lines, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `upi` on enums `CustomerListPaymentMethodsParams.type`, `PaymentMethodCreateParams.type`, a...

- **Entry ID:** `stripe_node-114`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to customer and payment method listing/creation parameters, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `quantity_decimal` on `InvoiceAddLinesParams.lines[]`, `InvoiceCreatePreviewParams.invoice_items[]`,...

- **Entry ID:** `stripe_node-115`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds `quantity_decimal` to invoice line items, explicitly marked as breaking and affecting billing and the data model.

#### 🟠 ⚠️ Add support for `level` on `Issuing.AuthorizationCreateParams.testHelpers.risk_assessment.card_testing_risk` and `...

- **Entry ID:** `stripe_node-116`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new field to Issuing Authorization risk assessment, explicitly marked as breaking and affecting billing and the data model.

#### 🟠 ⚠️ Remove support for `risk_level` on `Issuing.AuthorizationCreateParams.testHelpers.risk_assessment.card_testing_ris...

- **Entry ID:** `stripe_node-117`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry explicitly states the removal of the `risk_level` field from Issuing Authorization risk assessment, which is a breaking change with high risk affecting billing and the data model.

#### 🟡 Add support for `lifecycle_controls` on `Issuing.CardCreateParams` and `Issuing.Card`

- **Entry ID:** `stripe_node-118`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds lifecycle controls to Issuing Cards, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `Issuing.Token.network_data.visa.card_reference_id` from `string` to `string | null`

- **Entry ID:** `stripe_node-119`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `PaymentAttemptRecord.payment_method_details.card.brand` and `PaymentRecord.payment_method_details....

- **Entry ID:** `stripe_node-120`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `PaymentAttemptRecord.payment_method_details.card.exp_month` and `PaymentRecord.payment_method_deta...

- **Entry ID:** `stripe_node-121`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `PaymentAttemptRecord.payment_method_details.card.exp_year` and `PaymentRecord.payment_method_detai...

- **Entry ID:** `stripe_node-122`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `PaymentAttemptRecord.payment_method_details.card.funding` and `PaymentRecord.payment_method_detail...

- **Entry ID:** `stripe_node-123`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `PaymentAttemptRecord.payment_method_details.card.last4` and `PaymentRecord.payment_method_details....

- **Entry ID:** `stripe_node-124`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 ⚠️ Change type of `PaymentAttemptRecord.payment_method_details.card.moto` and `PaymentRecord.payment_method_details.c...

- **Entry ID:** `stripe_node-125`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `cryptogram`, `electronic_commerce_indicator`, `exemption_indicator_applied`, and `exemption_indicato...

- **Entry ID:** `stripe_node-126`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds new fields to 3D Secure payment method details, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for `upi_handle_redirect_or_display_qr_code` on `PaymentIntent.next_action` and `SetupIntent.next_action`

- **Entry ID:** `stripe_node-127`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new next action type for PaymentIntent and SetupIntent, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `upi` on enums `PaymentLink.payment_method_types`, `PaymentLinkCreateParams.payment_method_...

- **Entry ID:** `stripe_node-128`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new payment method type to PaymentLink objects, explicitly marked as breaking and affecting billing and the data model.

#### 🟠 Add support for `recommended_action` and `signals` on `Radar.PaymentEvaluation`

- **Entry ID:** `stripe_node-129`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds new fields to Radar PaymentEvaluation, explicitly marked as breaking and affecting billing and the data model.

#### 🟠 ⚠️ Remove support for `insights` on `Radar.PaymentEvaluation`

- **Entry ID:** `stripe_node-130`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry explicitly states the removal of the `insights` field from Radar PaymentEvaluation, which is a breaking change with high risk affecting billing and the data model.

#### 🟡 Add support for new value `crypto_fingerprint` on enums `Radar.ValueList.item_type` and `Radar.ValueListCreateParams....

- **Entry ID:** `stripe_node-131`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** This entry adds a new item type to Radar ValueList objects, explicitly marked as breaking and affecting the data model.

#### 🟡 Add support for new value `canceled_by_retention_policy` on enum `Subscription.cancellation_details.reason`

- **Entry ID:** `stripe_node-132`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds a new cancellation reason to a Subscription enum, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Add support for new value `2026-03-25.dahlia` on enum `WebhookEndpointCreateParams.api_version`

- **Entry ID:** `stripe_node-133`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** This entry adds support for a new API version in WebhookEndpoint creation parameters, explicitly marked as breaking and affecting the data model.

#### 🟠 ⚠️ Change type of `V2.Core.EventDestination.events_from` and `V2.Core.EventDestinationCreateParams.events_from` from...

- **Entry ID:** `stripe_node-134`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type from an enum to a string, explicitly marked as breaking and affecting the data model with high risk.

#### 🟡 Add support for error code `service_period_coupon_with_metered_tiered_item_unsupported` on `Invoice.last_finalization...

- **Entry ID:** `stripe_node-135`
- **Version:** 21.0.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry adds support for a new error code on various billing-related objects, explicitly marked as breaking and affecting billing and the data model.

#### 🟡 Change type of `PaymentAttemptRecord.payment_method_details.boleto.tax_id` and `PaymentRecord.payment_method_details....

- **Entry ID:** `stripe_node-148`
- **Version:** 20.4.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type to allow null, classifying it as a breaking change with medium risk that affects billing and the data model.

#### 🟡 Change type of `PaymentAttemptRecord.payment_method_details.us_bank_account.expected_debit_date` and `PaymentRecord.p...

- **Entry ID:** `stripe_node-149`
- **Version:** 20.4.0
- **Type:** breaking
- **Risk Level:** medium
- **Affects Auth:** False
- **Affects Billing:** True
- **Affects Data Model:** True
- **Rationale:** This entry changes a field type from nullable to non-nullable, classifying it as a breaking change with medium risk that affects billing and the data model.


### OpenAI Python SDK

#### 🟠 remove legacy python cli ([32f36e4](https://github.com/openai/openai-python/commit/32f36e447d02c3124af8ab48fcc3537df2...

- **Entry ID:** `openai_python-009`
- **Version:** 2.35.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** The removal of a "legacy python cli" is a backward-incompatible change that will break existing code relying on it.

#### 🟠 rename legacy python cli entrypoint ([a3b182d](https://github.com/openai/openai-python/commit/a3b182d6d2c2e6fe1d53ca7...

- **Entry ID:** `openai_python-010`
- **Version:** 2.35.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** False
- **Rationale:** Renaming a "legacy python cli entrypoint" is a backward-incompatible change that will break existing code relying on the old name.

#### 🟠 api: remove prompt_cache_key param from responses, phase field from message types ([44fb382](https://github.com/opena...

- **Entry ID:** `openai_python-095`
- **Version:** 2.25.0
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** This entry describes the removal of parameters and fields from API responses and message types, which is a backward-incompatible change that will break existing code and affects the data model.


### Twilio Changelog

#### 🟠 T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned

- **Entry ID:** `twilio-001`
- **Version:** T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** The retirement of specific warning error codes means existing integrations relying on these codes will no longer receive them, constituting a backward-incompatible change to the API's data model.

#### 🟠 T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned

- **Entry ID:** `twilio-003`
- **Version:** T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** The retirement of specific warning error codes means existing integrations relying on these codes will no longer receive them, constituting a backward-incompatible change to the API's data model.

#### 🟠 T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned

- **Entry ID:** `twilio-004`
- **Version:** T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** The retirement of specific warning error codes means existing integrations relying on these codes will no longer receive them, constituting a backward-incompatible change to the API's data model.

#### 🟠 T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned

- **Entry ID:** `twilio-005`
- **Version:** T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** The retirement of specific warning error codes means existing integrations relying on these codes will no longer receive them, constituting a backward-incompatible change to the API's data model.

#### 🟠 T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned

- **Entry ID:** `twilio-006`
- **Version:** T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** The retirement of specific warning error codes means existing integrations relying on these codes will no longer receive them, constituting a backward-incompatible change to the API's data model.

#### 🟠 Starting May 21, 2026, T-Mobile A2P 10DLC daily message cap warning error codes30025(50% threshold),30026(70% threshold)

- **Entry ID:** `twilio-008`
- **Version:** unknown
- **Type:** breaking
- **Risk Level:** high
- **Affects Auth:** False
- **Affects Billing:** False
- **Affects Data Model:** True
- **Rationale:** The retirement of specific warning error codes means existing integrations relying on these codes will no longer receive them, constituting a backward-incompatible change to the API's data model.


---

## Codebase Impact

**Snippet analyzed:** `codebase_snippet.py`

### ✅ `create_payment_intent`

- **Affected:** No
- **Detail:** The provided breaking changes are specific to the Stripe Node.js SDK (source_id: 'stripe_node'). This function is written in Python and uses the Stripe Python SDK, therefore it is not directly impacted by these Node.js SDK changes.
- **Suggested Fix:** No changes needed
- **Related Entries:** 

### ✅ `list_recent_charges`

- **Affected:** No
- **Detail:** The provided breaking changes are specific to the Stripe Node.js SDK (source_id: 'stripe_node'). This function is written in Python and uses the Stripe Python SDK, therefore it is not directly impacted by these Node.js SDK changes.
- **Suggested Fix:** No changes needed
- **Related Entries:** 

### ✅ `create_customer`

- **Affected:** No
- **Detail:** The provided breaking changes are specific to the Stripe Node.js SDK (source_id: 'stripe_node'). This function is written in Python and uses the Stripe Python SDK, therefore it is not directly impacted by these Node.js SDK changes.
- **Suggested Fix:** No changes needed
- **Related Entries:** 

---

## Migration Guides

No migration guides were generated (no affected functions).

---

## Unaffected Sources

All monitored sources had breaking or high-risk changes.

---

## Security Alerts

No security-related changes detected.

---

*Report generated by Changelog Monitoring Pipeline on 2026-05-13*
