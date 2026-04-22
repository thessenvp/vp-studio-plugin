# OptiTrack / Motion Capture Rules

## Equipment Specs

- **Software:** Motive 3.4.0.2
- **MoCap Cameras:** PrimeX41 x6, PrimeX22 x14 (IR)
- **Capture Space:** 11m x 6.5m x 3m
- **Effective Capture Area:** 9m x 5m
- **Max Simultaneous MoCap Actors:** 3

## MoCap Session File Naming Convention

**Pattern:** `{Project}_S{##}_C{##}_{MoCapCharacter}_{###}`

| Element | Description | Example |
|---|---|---|
| `Project` | Project name | `FilmA` |
| `S##` | Scene number | `S01` |
| `C##` | Cut number | `C03` |
| `MoCapCharacter` | Capture target character name | `HeroA` |
| `###` | Take number | `001` |

**Example:** `FilmA_S01_C03_HeroA_001`

## Reference

- OptiTrack Documentation: `https://docs.optitrack.com/`
- OptiTrack Camera Products: `https://optitrack.com/cameras`
