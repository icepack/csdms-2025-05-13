---
title: Glacier flow modeling with icepack
theme: solarized
---

<img src="https://icepack.github.io/images/logo.svg">

Daniel Shapero

University of Washington

Applied Physics Lab

shapero@uw.edu

----

### Plan

* Why we care about glaciers (10 min)
* Glaciology and glacier physics (35 min)
* The finite element method, Firedrake (20 min)
* Icepack demonstrations (45 min)



---

# Glaciology

----

### Why: sea-level rise

<img src="https://www.ipcc.ch/site/assets/uploads/sites/3/2019/10/IPCC-SROCC-CH_4_2-3000x1354.jpg">

<small>Sea-level rise projections, from IPCC</small>

----

### Marine ice sheet instability

<img src="https://www.ipcc.ch/site/assets/uploads/sites/3/2019/10/IPCC-SROCC-CH_4_8-3000x1028.jpg">

<small>Diagram of Thwaites Glacier, from IPCC</small>

----

### Why: water resources

<img src="https://www.nps.gov/articles/000/images/MORA-Stream-Temp_Fig1_web.jpeg?maxwidth=1300&autorotate=false&quality=78&format=webp" width="80%">

<small>Emmons Glacier on Mt. Rainier and the White River, from NPS</small>

----

### Why: paleoclimate

<iframe scrolling="no" frameborder="0" marginheight="0px" marginwidth="0px" style="display: initial; margin: 0 auto;" src="https://cbhighcharts2020.s3.eu-west-2.amazonaws.com/ice-age-co2/ice+age+co2+temps.html" width="770px" height="500px"></iframe><span style="display:block; height:22px; max-width:800px;"><a href="https://www.carbonbrief.org"><img src="https://s3.eu-west-2.amazonaws.com/cbhighcharts2019/cb-logo-highcharts.svg" style="width: 22px; height: 22px; margin-top: 2px; margin-bottom: 2px; float:right; background-repeat: no-repeat; background-size: contain;"/></a></span>

----

<img src="https://www.antarcticglaciers.org/wp-content/uploads/2013/10/icecore_4.jpg" width="75%">

<small>From Lonnie Thompson, Byrd Polar Research Center</small>

----

### Why: glacial geomorphology

<iframe width="560" height="315" src="https://www.youtube.com/embed/D5uDaEpJHjE?si=TTWdjbizJccEtSm3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

----

### Interlude

Let's play with some data!

[National snow and Ice Data Center](https://nsidc.org)



---

# Balance laws

----

### Big picture: ice flows downhill

<img src="https://www.antarcticglaciers.org/wp-content/uploads/2012/10/1024px-Glacier_in_Antarctica_Antarctic_Peninsula.jpg" width="75%">

<small>From AntarcticGlaciers.org</small>

----

### Cast of characters

| Variable | Symbol | Units | Type |
| -------- | ------ | ----- | ---: |
| thickness | $h$ | m | scalar |
| surface | $s$ | m | |
| temperature | $T$ | ${}^\circ K$ | |
| velocity | $u$ | m/yr | vector |
| bed stress | $\tau$ | kPa | |
| membrane stress | $M$ | kPa | tensor |
| strain rate | $\dot\varepsilon$ | 1/yr | |

----

### Mass balance

* thickness change + flux div = accumulation - melt
$$\partial\_t h + \nabla\cdot hu = \dot a - \dot m$$
* Accumulation & melt are functions of elevation.
* To know how fast mass is transported downslope, we need to understand momentum balance.

----

### Mechanics

* On long time and length scales (> 1 d, 100 m), glaciers flow like a viscous fluid.
* First identified in the 1840s by Forbes.
* Very low Reynolds number.

----

<iframe width="560" height="315" src="https://www.youtube.com/embed/YslhQZwvvu0?si=0e8BimEQXFGMc002" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<small>Time series of Malaspina Glacier, Alaska. From Bas Altena</small>

----

### Momentum balance

* Most principled model is the Stokes equations.
* In practice, we usually simplify based on:
  - low aspect ratio: thickness / length $\approx$ 1/20
  - simple stress regime: vertical shear flow in the interior, extension in ice streams

----

### Simplification

<img src="https://www.antarcticglaciers.org/wp-content/uploads/2015/03/SSA_SIA_coupling.png" width="35%"> <img src="https://www.antarcticglaciers.org/wp-content/uploads/2015/03/sliding-and-deformation-SIA_SSA-768x367.png" width="52%">

In simple stress regimes we can depth average.

----

### Shallow stream approximation

* The *membrane stress* tensor $M$ is what's left after perturbative simplification + depth averaging.
* Balance law:
$$\underbrace{\nabla\cdot hM}\_{\substack{\text{stress}\\\\ \text{divergence}}} + \underbrace{\tau}\_{\substack{\text{basal}\\\\ \text{drag}}} - \underbrace{\rho gh\nabla s}\_{\text{gravity}} = 0$$
* We still need to know how $M$ and $\tau$ relate to $u$!

----

### Glen's flow law

* For most fluids, stress $\propto$ strain rate.
* **Glaciers are not like most fluids:**
$$\text{stress} \propto \text{strain rate}^{1/n}$$
where $n \approx 3$.
* Glacier flow is **shear-thinning**.

----

### Glen's flow law

* Remember $\dot\varepsilon = \frac{\nabla u + \nabla u^\top}{2}$; the membrane stress is:
$$M = \mu\left\\{\dot\varepsilon + \text{tr}(\dot\varepsilon)I\right\\} \equiv 2\mu\mathscr{C}\dot\varepsilon$$
* ...where the viscosity is:
$$\mu = A^{-1/n}\sqrt{\frac{\dot\varepsilon : \dot\varepsilon + \text{tr}(\dot\varepsilon)^2}{2}}^{\frac{1}{n} - 1} = A^{-1/n}|\dot\varepsilon|\_{\mathscr{C}}^{\frac{1}{n} - 1}$$

----

### Sliding

* Ice can slide at its base.
Basal drag $\propto$ speed${}^{1/m}$:
$$\tau = -C|u|^{\frac{1}{m} - 1}u$$
$m$ is somewhere between $n$ and $\infty$, not really sure
* Basal friction depends on geology and hydrology -- subglacial hydrology is a "holy grail" problem.

----

### Sliding

<img src="https://www.antarcticglaciers.org/wp-content/uploads/2019/09/Dubawnt-Lake-MSGLs-1024x622.png" width="65%">

<small>From Stokes and Clark (2003), The Dubawnt Lake palaeo-ice stream: evidence for dynamic ice sheet behavior on the Canadian shield</small>

----

### Energy balance

* Finally, head conduction:
$$\partial\_t E + \nabla\cdot(Eu - k\nabla T) = Q$$
* Which feeds back into the momentum balance:
$$A \propto \exp(-Q / RT)$$

----

### The missing pieces

* **Sliding**
  - How does subglacial hydrology work?
  - How does it relate to basal drag?
* **Flow law**
  - Is $n = 3$?
    Are there more terms?
  - Is the flow law isotropic?
* **Calving**
  - How does it work at large scales?
  - Frequent and small vs rare and large



---

# Numerics

----

### Summary

* The things we need to get right:
  - $h$ $\rightarrow$ climate $\rightarrow$ $\dot a$, $\dot m$
  - $u$, $h$ $\rightarrow$ mass balance $\rightarrow$ $dh/dt$
  - $h$, $T$ $\rightarrow$ momentum balance $\rightarrow$ $u$
  - $u$, $h$, $T$ $\rightarrow$ energy balance $\rightarrow$ $dT/dt$
* This is a big differential-algebraic equation.
* We can do all this with the finite element method.

----

### Requirements

* Physical scientists want solvers for the mass, momentum, energy balance equations.
* They will also want to:
  - do weird things with flow and sliding laws
  - couple to other fields, e.g. hydrology, landscape
* **How do we make modeling tools that are both flexible and user-friendly?**

----

### The finite element method

* Students are familiar, but often uncomfortable, with differential equations.
* The finite element method uses variational forms.
* **We have a pedagogy problem.**

----

### Numerics

* A typical numerical scheme uses operator splitting:
```python
for step in range(num_steps):
    h = mass_balance_solve(dt, thickness=h, velocity=u, ...)
    u = momentum_balance_solve(velocity=u, thickness=h, ...)
    T = energy_balance_solve(temperature=T, velocity=u, ...)
```
* Things we're working on:
  - How to make sure the thickness is positive?
  - Can we get higher order w/monolithic schemes?

----

<img src="https://icepack.github.io/images/logo.svg">

* Software package for simulating glaciers in Python
* Built on the finite element modeling library Firedrake

----

### Problems

* Bad things happen when $\dot\varepsilon \to 0$ or $h \to 0$.
* When $\dot\varepsilon \to 0$, $\mu \to \infty$.
So we regularize:
$$\mu = A^{-1/n}\sqrt{|\dot\varepsilon|\_{\mathscr{C}}^2 + \dot\varepsilon\_0^2}^{\frac{1}{n} - 1}$$
* $h \to 0$ is a singular perturbation (yikes).
* It also tends to make $\dot\varepsilon \to 0$.

----

### Missing pieces

* How can we best couple all the conservation laws?
* What do we do around 0 velocity or strain rate?
* **What are the right numerics for calving?**



---

# Terminus evolution

----

<iframe width="560" height="315" src="https://www.youtube.com/embed/TWGR6FxFlt8?si=rTZGByPomHoLMCWy" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

LeConte Glacier, Alaska

----

Simulation of Kangerlussuaq Glacier, SE Greenland

<iframe width="560" height="315" src="https://www.youtube.com/embed/01Kvp7Hoego?si=Jv3x-cdhmf6xo_dp" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>



---

# Conclusions

----

### Conclusions

* Problems with similar characteristics:
  - glaciers
  - lava
  - overland water flow
  - unsaturated porous media
  - plankton growth
* Are there common numerical approaches?

----

### Help

If you're interested in this kind of thing:

shapero@uw.edu

[icepack.github.io](https://icepack.github.io/)

----

Go to an icefield:

<center><img src="https://icepack.github.io/images/JIRP-logo.jpg" width="40%"></center>

www.juneauicefield.org

----

<img src="20220705_125636.jpg">

----

<img src="gps-survey-all.png">

----

<img src="20220715_121712.jpg">
