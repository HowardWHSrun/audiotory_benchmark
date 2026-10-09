# Hardware budget verification

October 9, 2026. Scope: hardware research and a parts budget based on the two supplied slides. No website source or manuscript edits.

- Copied the supplied PNGs unchanged into the source register. SHA256 for the system diagram: `939f91ed04072a9c9081320d206136c35656190778648ffbe4a637c52905d991`. SHA256 for the equipment links: `83f54973833acb7e2c9a279918a688f66fd11909f95f2cf5981b2a366e5cf36e`.
- Opened the primary eBay listing pages used for the lower acoustic basket and NI/TDT price leads. The refreshed ED1/power bundle displayed $209.06; this is the value used in the final budget. Cached/locale-dependent shipping and delivery dates were not treated as Houston quotations.
- Manufacturer checks distinguish audible-band components from ES1 ultrasound, ES1 power/driver dependencies, the PXI-4461 hybrid-slot variant, the output sampling/bandwidth limit, Avisoft 40026 kit contents and external power, USB DAQ alternatives and shared-marker synchronization.
- A separate review found and corrected a $500 error in the high rack subtotal before authoring. A second review confirmed the final scientific/compatibility distinctions and corrected the description of the three-part basket so it does not imply a complete validated experiment.
- Spreadsheet calculations use linked input prices, quantity times unit cost, subtotal and reserve formulas. Independent arithmetic agrees with all four option totals. Increasing one real input price by $10 changed the applicable summary by $10; the input was restored. The final formula-error scan found no errors.
- Visually reviewed both workbook sheets, including the summary, the minimum basket, mixed listing/estimate rows and long source URLs. Removed unwanted cell-grid borders. Numbers, conditions and source text are readable. Workbook recalculation/export were checked with the artifact authoring engine; native Microsoft Excel behavior was not separately tested.
- Six existing scientific-model checks passed. Both browser code files passed syntax validation. Repository source/link validation and static-site build passed, with the pinned SONIC v1 PDF checksum unchanged. Diff whitespace checks passed. Browser interaction checks were not repeated because no website source changed.
- The budgets describe one sound channel using the lab neural chain. All calibration, synchronization, unquoted speaker/driver, support and reserve inputs are labeled as assumptions or estimates. The approximately $30,000 high scenario is not a market ceiling or a manufacturer quotation.

No vendor contact, order, equipment connection, acoustic test, neural recording or animal procedure was performed. Temporary authoring files, spreadsheet renders and inspection output remain outside the repository.
