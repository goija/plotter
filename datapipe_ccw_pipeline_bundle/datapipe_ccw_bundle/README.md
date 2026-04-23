# Datapipe CCW bundle

This bundle rewrites the staged datapipe around a canonical de Bruijn / Lyndon model.

Main model additions:
- canonical lexicographically least de Bruijn cycle via Lyndon/FKM construction
- state-based disturbance channels for weather and atmospheric data
- combined disturbance using `c` in 11 datapoints: `0.0, 0.1, ..., 1.0`
- continuous color weight field `ccw` for plots/graphics
- discrete report fields `dominance_case` and `color`
- red reserved for operational errors only
