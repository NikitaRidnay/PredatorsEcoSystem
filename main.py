import pygame
import random
import math

from datetime import datetime

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Predators")

font = pygame.font.SysFont('Andale Mono', 15)
NAMES = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta",
         "Eta", "Theta", "Iota", "Kappa", "Lambda", "Mu", "IO", "R1", "DSA"]

SESSION_TIME = 60
start_time = pygame.time.get_ticks()

creature_counts = []
average_energies = []
family_data = {}


class Creature:
    def __init__(self, x, y, name=None, color=None, parent=None):
        self.x = x
        self.y = y
        self.energy = 100
        self.size = random.uniform(15, 40)
        self.speed = random.uniform(1, 3)
        self.name = (name or random.choice(NAMES))[:10]
        self.color = color or (random.randint(0, 255),
                               random.randint(0, 255),
                               random.randint(0, 255))
        self.attack_range = self.size * 1.5
        self.parent = parent
        self.eaten_count = 0

        if self.name not in family_data:
            family_data[self.name] = {
                'total_eaten': 0,
                'max_energy': self.energy,
                'creatures': []
            }

    def find_target(self, creatures):
        targets = [c for c in creatures if c != self and
                   c.parent != self and c != self.parent and
                   c.size < self.size * 0.8]
        return min(targets, key=lambda t: math.hypot(t.x - self.x, t.y - self.y), default=None)

    def move(self, creatures):
        target = self.find_target(creatures)
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            distance = math.hypot(dx, dy)

            if distance > 0:
                move_x = dx / distance * self.speed
                move_y = dy / distance * self.speed

                self.x = max(self.size, min(WIDTH - self.size, self.x + move_x))
                self.y = max(self.size, min(HEIGHT - self.size, self.y + move_y))

                if distance < self.size * 0.5:
                    self.eat(target)
                    creatures.remove(target)

        self.energy -= 0.4 + self.size / 30

    def eat(self, prey):
        self.energy += prey.energy * 0.7
        self.size += prey.size * 0.2
        self.speed = max(0.5, self.speed - 0.05)
        self.energy = min(180, self.energy)
        self.eaten_count += 1
        family_data[self.name]['total_eaten'] += 1
        family_data[self.name]['max_energy'] = max(family_data[self.name]['max_energy'], self.energy)

    def reproduce(self):
        child = Creature(self.x, self.y, parent=self)
        child.size = self.size * random.uniform(0.8, 1.2)
        child.speed = self.speed * random.uniform(0.9, 1.1)
        child.name = f"{self.name}.ch"[:15]
        child.color = self.color
        return child


def save_session():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"family_performance_{timestamp}.txt"

    with open(filename, 'w') as f:
        f.write("Family Performance Summary:\n")
        f.write(f"{'Family Name':<15} | {'Total Eaten':^12} | {'Max Energy':^12}\n")
        f.write("-" * 45 + "\n")

        family_summary = []
        for name, data in family_data.items():
            family_summary.append({
                'Family': name,
                'Total Eaten': data['total_eaten'],
                'Max Energy': data['max_energy']
            })

        family_summary.sort(key=lambda x: x['Max Energy'], reverse=True)

        for family in family_summary:
            f.write(f"{family['Family']:<15} | {family['Total Eaten']:^12} | {family['Max Energy']:^12.1f}\n")

    print(f"Session saved as {filename}")


def analyze_session():
    # Analyze family performance
    family_summary = []
    for name, data in family_data.items():
        family_summary.append({
            'Family': name,
            'Total Eaten': data['total_eaten'],
            'Max Energy': data['max_energy']
        })

    family_summary.sort(key=lambda x: x['Max Energy'], reverse=True)

    print("\n" + "=" * 50)
    print("Family Performance Summary:")
    print(f"{'Family Name':<15} | {'Total Eaten':^12} | {'Max Energy':^12}")
    print("-" * 45)
    for family in family_summary[:5]:
        print(f"{family['Family']:<15} | {family['Total Eaten']:^12} | {family['Max Energy']:^12.1f}")
    print("=" * 50 + "\n")


def main():
    clock = pygame.time.Clock()
    creatures = [Creature(random.uniform(0, WIDTH),
                          random.uniform(0, HEIGHT)) for _ in range(30)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_creatures = list(creatures)

        creature_counts.append(len(creatures))
        avg_energy = sum(c.energy for c in creatures) / len(creatures) if creatures else 0
        average_energies.append(avg_energy)

        for creature in current_creatures:
            if creature in creatures:
                creature.move(creatures)
                if creature.energy <= 0:
                    creatures.remove(creature)
                elif creature.energy >= 180:
                    creatures.append(creature.reproduce())
                    creature.energy = 80

        if len(creatures) < 20:
            creatures.append(Creature(
                random.uniform(0, WIDTH),
                random.uniform(0, HEIGHT),
                name=random.choice(NAMES),
                color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            ))

        screen.fill((25, 25, 40))
        for creature in creatures:
            pygame.draw.circle(screen, creature.color,
                               (int(creature.x), int(creature.y)),
                               int(creature.size))
            pygame.draw.circle(screen, (255, 255, 255),
                               (int(creature.x), int(creature.y)),
                               int(creature.size), 1)

            energy_ratio = creature.energy / 180
            pygame.draw.rect(screen, (150, 150, 150),
                             (creature.x - 25, creature.y + creature.size + 5, 50, 4))
            pygame.draw.rect(screen, (50, 200, 50),
                             (creature.x - 25, creature.y + creature.size + 5, 50 * energy_ratio, 4))

            name_surface = font.render(creature.name, True, (255, 255, 255), (30, 30, 30))
            text_rect = name_surface.get_rect(center=(creature.x, creature.y + creature.size + 20))
            screen.blit(name_surface, text_rect)

        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
        remaining_time = max(0, SESSION_TIME - elapsed_time)
        timer_surface = font.render(f'Time left: {int(remaining_time)}s', True, (255, 255, 255))
        screen.blit(timer_surface, (WIDTH - 150, 10))

        if remaining_time <= 0:
            running = False

        pygame.display.flip()
        clock.tick(30)

    save_session()
    analyze_session()
    pygame.quit()


if __name__ == "__main__":
    main()